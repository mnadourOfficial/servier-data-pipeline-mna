SELECT
    date,
    SUM(prod_price * prod_qty) AS ventes
FROM
    `GCP_PROJECT_ID.DATASET_NAME.TRANSACTIONS`
WHERE
    date BETWEEN DATE("2019-01-01") AND DATE("2019-12-31")
GROUP BY
    date
ORDER BY
    date