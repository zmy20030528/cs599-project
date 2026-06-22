param(
    [string]$DocxPath = "docs\report.docx",
    [string]$PdfPath = "docs\report.pdf"
)

$ErrorActionPreference = "Stop"
$docx = [string]((Get-Item -LiteralPath $DocxPath).FullName)
$pdf = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($PdfPath)
$docDir = Split-Path -Parent $docx
$tempDocx = Join-Path $docDir "_cs599_report_export2.docx"
$tempPdf = Join-Path $docDir "_cs599_report_export2.pdf"
Copy-Item -LiteralPath $docx -Destination $tempDocx -Force
$word = $null
$doc = $null

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    Write-Output "Opening DOCX..."
    $doc = $word.Documents.Open($tempDocx)

    $doc.Content.Font.NameFarEast = "Microsoft YaHei"
    # Built-in style -2 is Heading 1; applying once is much faster than COM paragraph iteration.
    $doc.Styles.Item(-2).ParagraphFormat.PageBreakBefore = -1
    $doc.Styles.Item(-2).ParagraphFormat.KeepWithNext = -1

    $tocRange = $doc.Content.Duplicate
    $tocRange.Find.Text = "[[TOC]]"
    if (-not $tocRange.Find.Execute()) {
        throw "未找到目录占位符 [[TOC]]"
    }
    Write-Output "Building TOC..."
    $tocRange.Text = ""
    [void]$doc.TablesOfContents.Add($tocRange, $true, 1, 3, $false, "", $true, $true, "", $true, $true, $true)
    [void]$doc.Fields.Update()
    foreach ($toc in $doc.TablesOfContents) { [void]$toc.Update() }

    $doc.Save()
    Write-Output "Exporting PDF..."
    # 17=PDF, 0=print optimization, 1=create bookmarks from headings.
    $doc.ExportAsFixedFormat($tempPdf, 17, $false, 0, 0, 1, 1, 0, $true, $true, 1, $true, $true, $false)
    Write-Output "PDF export complete."
}
finally {
    if ($doc -ne $null) { $doc.Close($false) }
    if ($word -ne $null) { $word.Quit() }
    if ($doc -ne $null) { [void][Runtime.InteropServices.Marshal]::ReleaseComObject($doc) }
    if ($word -ne $null) { [void][Runtime.InteropServices.Marshal]::ReleaseComObject($word) }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

if (Test-Path -LiteralPath $tempPdf) { Copy-Item -LiteralPath $tempPdf -Destination $pdf -Force }
Remove-Item -LiteralPath $tempDocx -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath $tempPdf -Force -ErrorAction SilentlyContinue

Get-Item $pdf | Select-Object FullName, Length, LastWriteTime
