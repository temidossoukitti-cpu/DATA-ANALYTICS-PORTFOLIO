// Create a Power Query text parameter named CsvPath before using this query.
// Example value:
// C:\Users\YourName\DATA-ANALYTICS-PORTFOLIO\projects\03-ventes-retail\data\processed\superstore_clean.csv

let
    Source = Csv.Document(
        File.Contents(CsvPath),
        [
            Delimiter = ",",
            Columns = 22,
            Encoding = 65001,
            QuoteStyle = QuoteStyle.Csv
        ]
    ),
    PromotedHeaders = Table.PromoteHeaders(
        Source,
        [PromoteAllScalars = true]
    ),
    TypedColumns = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"Row ID", Int64.Type},
            {"Order ID", type text},
            {"Order Date", type date},
            {"Ship Date", type date},
            {"Ship Mode", type text},
            {"Customer ID", type text},
            {"Customer Name", type text},
            {"Segment", type text},
            {"Country", type text},
            {"City", type text},
            {"State", type text},
            {"Postal Code", type text},
            {"Region", type text},
            {"Product ID", type text},
            {"Category", type text},
            {"Sub-Category", type text},
            {"Product Name", type text},
            {"Sales", type number},
            {"Quantity", Int64.Type},
            {"Discount", type number},
            {"Profit", type number},
            {"Potential Duplicate", type logical}
        },
        "en-US"
    )
in
    TypedColumns
