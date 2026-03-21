import math


def _decode_redis_map(hm):
    """Convert a redis HGETALL mapping (bytes->bytes or str->str) to str->str dict"""
    out = {}
    for k, v in hm.items():
        if isinstance(k, bytes):
            k = k.decode("utf-8")
        if isinstance(v, bytes):
            v = v.decode("utf-8")
        out[k] = v
    return out


def create_index(r, index_name="cards-idx"):
    """Create a RediSearch index for card hashes stored with prefix `card:`.

    Fields:
    - code: TEXT
    - name: TEXT
    - faction_code: TAG (separator `|`)
    - traits: TAG (separator `|`)
    - xp: NUMERIC
    """
    # try drop if exists
    try:
        r.execute_command("FT.DROPINDEX", index_name)
    except Exception:
        pass

    # Create index on HASH with prefix card:
    # FT.CREATE idx ON HASH PREFIX 1 card: SCHEMA code TEXT name TEXT faction_code TAG SEPARATOR | traits TAG SEPARATOR | xp NUMERIC
    try:
        r.execute_command(
            "FT.CREATE",
            index_name,
            "ON",
            "HASH",
            "PREFIX",
            "1",
            "card:",
            "SCHEMA",
            "code",
            "TEXT",
            "name",
            "TEXT",
            "faction_code",
            "TAG",
            "SEPARATOR",
            "|",
            "traits",
            "TAG",
            "SEPARATOR",
            "|",
            "xp",
            "NUMERIC",
        )
    except Exception as e:
        # In some RediSearch versions, SEPARATOR must be right after TAG; the command above should work in modern Redis modules.
        # If creation failed, re-raise the exception so the test fixture can skip if needed.
        raise


def _search_query(r, index_name, query, offset=0, page_size=10):
    """Run FT.SEARCH and return (total, [docid,...])"""
    # run search
    resp = r.execute_command("FT.SEARCH", index_name, query, "LIMIT", str(offset), str(page_size))
    if not resp:
        return 0, []
    total = int(resp[0]) if isinstance(resp[0], (int,)) else int(resp[0])
    ids = []
    # resp structure: [total, id1, fields1_array, id2, fields2_array, ...]
    i = 1
    while i < len(resp):
        docid = resp[i]
        # sometimes docid is bytes
        if isinstance(docid, bytes):
            docid = docid.decode("utf-8")
        ids.append(docid)
        i += 2
    return total, ids


def search_by_factions(r, factions, mode="OR", page=0, page_size=10, index_name="cards-idx"):
    """Search cards by faction list.

    mode: 'OR' or 'AND'
    Returns dict {"total": int, "results": [hm, ...]}
    """
    if not factions:
        query = "*"
    else:
        # factions are TAG field values; build TAG query
        if mode.upper() == "OR":
            q = "|".join(factions)
            query = f"@faction_code:{{{q}}}"
        else:
            parts = [f"@faction_code:{{{f}}}" for f in factions]
            query = " ".join(parts)

    offset = page * page_size
    total, ids = _search_query(r, index_name, query, offset=offset, page_size=page_size)
    results = []
    for _id in ids:
        hm = r.hgetall(_id)
        results.append(_decode_redis_map(hm))
    return {"total": total, "results": results}


def top_traits_for_faction(r, faction, page=0, page_size=10, index_name="cards-idx"):
    """Return top traits for a given faction by simple in-memory aggregation (small dataset expected)."""
    # get a reasonably large page to compute top traits; for tests small dataset is enough
    res = search_by_factions(r, [faction], mode="OR", page=0, page_size=100, index_name=index_name)
    counts = {}
    for d in res["results"]:
        traits = d.get("traits", "")
        if not traits:
            continue
        for t in str(traits).split("|"):
            t = t.strip()
            if not t:
                continue
            counts[t] = counts.get(t, 0) + 1
    items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    # paginate results
    start = page * page_size
    end = start + page_size
    return {"faction": faction, "results": items[start:end], "total": len(items)}


def search_upgrades(
    r,
    traits=None,
    preferred_faction=None,
    xp_max=None,
    page=0,
    page_size=5,
    index_name="cards-idx",
):
    """Search upgradeable cards matching given traits and xp filters.

    Behavior implemented per spec:
    - Only cards with xp > 0 are considered.
    - Exclude faction `mythos` always.
    - Prefer (boost) cards from `preferred_faction` so they surface earlier.
    - Allow matching traits (TAG field) - if None, ignored.
    - Filter by xp_max if provided: xp in [1, xp_max]
    - Pagination default 5

    Returns: {"total_cards": int, "results": [hash maps], "page": page, "page_size": page_size}
    """
    parts = []
    # traits: TAG field syntax
    if traits:
        # traits can be list or comma-separated string
        if isinstance(traits, (list, tuple)):
            tr = "|".join(traits)
        else:
            tr = str(traits)
        parts.append(f"@traits:{{{tr}}}")

    # xp filter: require > 0
    if xp_max is not None:
        parts.append(f"@xp:[1 {int(xp_max)}]")
    else:
        parts.append("@xp:[1 +inf]")

    # exclude mythos
    parts.append("-@faction_code:{mythos}")

    # preferred faction boost (optional)
    if preferred_faction:
        parts.append(f"(@faction_code:{{{preferred_faction}}})^5")

    base_query = " ".join(parts) if parts else "*"

    offset = page * page_size
    total, ids = _search_query(r, index_name, base_query, offset=offset, page_size=page_size)

    results = []
    for _id in ids:
        hm = r.hgetall(_id)
        results.append(_decode_redis_map(hm))

    return {
        "total_cards": total,
        "results": results,
        "page": page,
        "page_size": page_size,
    }
