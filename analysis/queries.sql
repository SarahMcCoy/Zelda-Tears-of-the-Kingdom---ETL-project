-- 1) What acquisition categories exist?
SELECT acquisition_category, COUNT(*) AS count
FROM armor
GROUP BY acquisition_category
ORDER BY count DESC;

-- 2) Top base defense items
SELECT name, defense_base, equip_slot
FROM armor
ORDER BY defense_base DESC
LIMIT 15;

-- 3) Top max defense items
SELECT name, defense_max, equip_slot
FROM armor
ORDER BY defense_max DESC
LIMIT 15;

-- 4) Best defense-per-rupee (base)
SELECT name, defense_base, buy_price_rupees, defense_per_rupee
FROM armor
WHERE defense_per_rupee IS NOT NULL
ORDER BY defense_per_rupee DESC
LIMIT 15;

-- 5) Best max-defense-per-rupee (investment)
SELECT name, defense_max, buy_price_rupees, max_defense_per_rupee
FROM armor
WHERE max_defense_per_rupee IS NOT NULL
ORDER BY max_defense_per_rupee DESC
LIMIT 15;

-- 6) Effects inventory (what effects exist?)
SELECT effect, COUNT(*) AS count
FROM armor
WHERE effect IS NOT NULL
GROUP BY effect
ORDER BY count DESC;