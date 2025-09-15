/*
 * Calcule les ventes par client pour les catégories 'MEUBLE' et 'DECO'
 * sur la période du 1er janvier 2020 au 31 décembre 2020.
 */
SELECT
    t.client_id,
    -- Agrégation conditionnelle pour les ventes de meubles
    -- On somme le montant (prix * quantité) uniquement si le type est 'MEUBLE'
    SUM(CASE WHEN pn.product_type = 'MEUBLE' THEN t.prod_price * t.prod_qty ELSE 0 END) AS ventes_meuble,
    -- Agrégation conditionnelle pour les ventes de décoration
    SUM(CASE WHEN pn.product_type = 'DECO' THEN t.prod_price * t.prod_qty ELSE 0 END) AS ventes_deco
FROM
    `GCP_PROJECT_ID.DATASET_NAME.TRANSACTIONS` AS t
-- Jointure pour récupérer le type de produit depuis la table de nomenclature
JOIN
    `GCP_PROJECT_ID.DATASET_NAME.PRODUCT_NOMENCLATURE` AS pn ON t.prod_id = pn.product_id
WHERE
    -- Filtrage sur la période demandée
    t.date >= '2020-01-01' AND t.date <= '2020-12-31'
GROUP BY
    -- Agrégation par client
    t.client_id
ORDER BY
    t.client_id