function AuditTable({ records }) {
  if (!records || records.length === 0) {
    return null;
  }

  const formatTimestamp = (timestamp) => {
    if (!timestamp) {
      return "-";
    }

    const date = new Date(timestamp);

    if (Number.isNaN(date.getTime())) {
      return timestamp;
    }

    return date.toLocaleString("en-IN", {
      timeZone: "Asia/Kolkata",
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: true,
    });
  };

  return (
    <div className="audit-table-wrapper">
      <div className="audit-table-title">Audit History</div>

      <div className="audit-table-scroll">
        <table className="audit-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Actor</th>
              <th>Action</th>
              <th>Resource</th>
              <th>Target</th>
              <th>Details</th>
            </tr>
          </thead>

          <tbody>
            {records.map((record) => (
              <tr key={record.id}>
                <td>{formatTimestamp(record.timestamp)}</td>

                <td>{record.actor || "-"}</td>

                <td>
                  <span className="audit-action">{record.action || "-"}</span>
                </td>

                <td>{record.resource || "-"}</td>

                <td>
                  {record.target_user
                    ? record.target_username
                      ? `${record.target_user} (${record.target_username})`
                      : record.target_user
                    : "-"}
                </td>

                <td>{record.details || "No details"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default AuditTable;
