// Função reutilizada por todas as tabelas: lê um CSV UTF-8 separado por vírgula e promove cabeçalhos.
(arquivo as text) as table =>
let
    Origem   = Csv.Document(File.Contents(PastaDados & arquivo), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promover = Table.PromoteHeaders(Origem, [PromoteAllScalars = true])
in
    Promover
