import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { apiFetch } from "./api";

interface PlayerStatRow {
  mp_id: string;
  player_name: string;
  team_name: string;
  runs: number;
  run_rate: number;
  econ: number;
  wickets: number;
  sixes: number;
  fours: number;
  catches: number;
}

export default function AdminMatchStats() {
  const { matchId } = useParams();
  const [rows, setRows] = useState<PlayerStatRow[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    const res = await apiFetch(`matches/${matchId}/stats/`);
    setRows(res.players);
    setLoading(false);
  };

  useEffect(() => {
    load();
  }, [matchId]);

  const updateValue = (
    index: number,
    field: keyof PlayerStatRow,
    value: number
  ) => {
    const copy = [...rows];
    copy[index] = { ...copy[index], [field]: value };
    setRows(copy);
  };

  const handleSave = async () => {
    await apiFetch(`matches/${matchId}/stats/`, {
      method: "POST",
      body: JSON.stringify({ players: rows }),
    });

    alert("Stats saved");
  };

  if (loading) return <p>Loading players...</p>;

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">
        Enter / Edit Player Stats
      </h2>

      <table className="w-full border">
        <thead>
          <tr className="bg-gray-100">
            <th>Player</th>
            <th>Team</th>
            <th>Runs</th>
            <th>Run Rate</th>
            <th>Economy</th>
            <th>Wickets</th>
            <th>Sixes</th>
            <th>Fours</th>
            <th>Catches</th>
          </tr>
        </thead>

        <tbody>
          {rows.map((p, i) => (
            <tr key={p.mp_id} className="border-t">
              <td>{p.player_name}</td>
              <td>{p.team_name}</td>

              <td>
                <input type="number"
                  value={p.runs}
                  onChange={e => updateValue(i,"runs",+e.target.value)}
                />
              </td>

              <td>
                <input type="number"
                  value={p.run_rate}
                  onChange={e => updateValue(i,"run_rate",+e.target.value)}
                />
              </td>

              <td>
                <input type="number"
                  value={p.econ}
                  onChange={e => updateValue(i,"econ",+e.target.value)}
                />
              </td>

              <td>
                <input type="number"
                  value={p.wickets}
                  onChange={e => updateValue(i,"wickets",+e.target.value)}
                />
              </td>

              <td>
                <input type="number"
                  value={p.sixes}
                  onChange={e => updateValue(i,"sixes",+e.target.value)}
                />
              </td>

              <td>
                <input type="number"
                  value={p.fours}
                  onChange={e => updateValue(i,"fours",+e.target.value)}
                />
              </td>

              <td>
                <input type="number"
                  value={p.catches}
                  onChange={e => updateValue(i,"catches",+e.target.value)}
                />
              </td>

            </tr>
          ))}
        </tbody>
      </table>

      <button
        onClick={handleSave}
        className="mt-4 bg-red-600 text-white px-4 py-2 rounded"
      >
        Save Stats
      </button>
    </div>
  );
}
