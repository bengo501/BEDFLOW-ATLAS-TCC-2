export default function OverrideDiffTable({ diff, t }) {
  if (!diff?.length) {
    return (
      <p className="bed-load-diff-empty">{t('bedLoadDiffEmpty')}</p>
    );
  }
  return (
    <table className="bed-load-diff-table">
      <thead>
        <tr>
          <th>{t('bedLoadDiffField')}</th>
          <th>{t('bedLoadDiffFrom')}</th>
          <th>{t('bedLoadDiffTo')}</th>
        </tr>
      </thead>
      <tbody>
        {diff.map((row) => (
          <tr key={row.path}>
            <td>{row.path}</td>
            <td>{JSON.stringify(row.from)}</td>
            <td>{JSON.stringify(row.to)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
