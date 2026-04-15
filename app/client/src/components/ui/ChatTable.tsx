type ChatTableProps = {
    columns: string[]
    rows: Array<Record<string, unknown>>
}

const formatCellValue = (value: unknown) => {
    if (value === null || value === undefined) {
        return '-'
    }
    if (typeof value === 'boolean') {
        return value ? 'true' : 'false'
    }
    return String(value)
}

export const ChatTable = ({ columns, rows }: ChatTableProps) => {
    if (!columns.length) {
        return (
            <p className="text-sm text-slate-500">
                No hay columnas para mostrar.
            </p>
        )
    }

    if (!rows.length) {
        return (
            <p className="text-sm text-slate-500">
                La consulta no devolvio filas.
            </p>
        )
    }

    return (
        <div className="max-w-full overflow-x-auto rounded-xl border border-slate-200 bg-white">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
                <thead className="bg-slate-50">
                    <tr>
                        {columns.map((column) => (
                            <th
                                key={column}
                                className="whitespace-nowrap px-3 py-2 text-left font-semibold text-slate-700"
                                scope="col"
                            >
                                {column}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                    {rows.map((row, index) => (
                        <tr key={`row-${index}`} className="align-top">
                            {columns.map((column) => (
                                <td key={`${column}-${index}`} className="whitespace-nowrap px-3 py-2 text-slate-700">
                                    {formatCellValue(row[column])}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}
