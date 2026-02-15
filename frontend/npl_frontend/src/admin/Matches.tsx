import { useEffect, useState } from "react";
import { apiFetch } from "./api";
import { useNavigate } from "react-router-dom";


interface Match {
  id: number;
  teams: string;
  match_date: string;
  status: string;
  team_1?: number; // needed for edit
  team_2?: number; // needed for edit
}

interface Team {
  team_id: number;
  team_name: string;
}

export default function Matches() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  const [team1, setTeam1] = useState(0);
  const [team2, setTeam2] = useState(0);
  const [date, setDate] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);

  const navigate = useNavigate();

  const fetchMatches = async () => {
  const res = await apiFetch("matches/");
  console.log("MATCH API RESPONSE:", res);
  setMatches(res.matches);
  };


  const fetchTeams = async () => {
    const res = await apiFetch("teams/");
    setTeams(res.teams);
    if (res.teams.length) {
      setTeam1(res.teams[0].team_id);
      setTeam2(res.teams[0].team_id);
    }
  };

  useEffect(() => {
    fetchMatches();
    fetchTeams();
  }, []);

  const resetForm = () => {
    setEditingId(null);
    setDate("");
    if (teams.length) {
      setTeam1(teams[0].team_id);
      setTeam2(teams[0].team_id);
    }
  };

  const handleAdd = async () => {
    await apiFetch("matches/add/", {
      method: "POST",
      body: JSON.stringify({
        match_date: date,
        team_1: team1,
        team_2: team2,
      }),
    });

    resetForm();
    fetchMatches();
  };

  const handleUpdate = async () => {
    if (!editingId) return;

    await apiFetch(`matches/${editingId}/edit/`, {
      method: "PUT",
      body: JSON.stringify({
        match_date: date,
        team_1: team1,
        team_2: team2,
      }),
    });

    resetForm();
    fetchMatches();
  };

  const handleDelete = async (id: number) => {
  try {
    const res = await apiFetch(`matches/${id}/delete/`, {
      method: "DELETE",
    });

    console.log("Delete response:", res);
    fetchMatches();
  } catch (err) {
    console.error("Delete failed:", err);
    alert("Delete failed — check console");
  }
};

const handleCalculate = async (id: number) => {

  if (!confirm("Calculate results for this match?")) return;
  try {
    const res = await apiFetch(`matches/${id}/calculate_result/`, {
      method: "POST",
      credentials: "include",
    });


    alert(`Results calculated for ${res.teams_processed} teams`);

  } catch (err) {
    console.error("Calculation failed:", err);
    alert("Calculation failed — check console");
  }
};


  const handleEdit = (m: Match) => {
    setEditingId(m.id);
    setDate(m.match_date);

    if (m.team_1) setTeam1(m.team_1);
    if (m.team_2) setTeam2(m.team_2);
  };

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Matches</h2>

      <div className="flex gap-2 mb-4">
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="border px-2 py-1 rounded"
        />

        <select
          value={team1}
          onChange={(e) => setTeam1(+e.target.value)}
          className="border px-2 py-1 rounded"
        >
          {teams.map((t) => (
            <option key={t.team_id} value={t.team_id}>
              {t.team_name}
            </option>
          ))}
        </select>

        <select
          value={team2}
          onChange={(e) => setTeam2(+e.target.value)}
          className="border px-2 py-1 rounded"
        >
          {teams.map((t) => (
            <option key={t.team_id} value={t.team_id}>
              {t.team_name}
            </option>
          ))}
        </select>

        <button
          onClick={editingId ? handleUpdate : handleAdd}
          className="bg-red-600 text-white px-4 py-1 rounded"
        >
          {editingId ? "Update" : "Add"}
        </button>

        {editingId && (
          <button
            onClick={resetForm}
            className="border px-3 py-1 rounded"
          >
            Cancel
          </button>
        )}
      </div>

      <ul className="space-y-2">
        {matches.map((m) => (
          <li
            key={m.id}
            className="flex justify-between bg-gray-100 p-2 rounded"
          >
            <span>
              {m.match_date} – {m.teams} ({m.status})
            </span>

            <div className="flex gap-3">
              <button
                onClick={() => handleEdit(m)}
                className="text-blue-600"
              >
                Edit
              </button>

              <button
                onClick={() => handleDelete(m.id)}
                className="text-red-600"
              >
                Delete
              </button>
              <button
                onClick={() => navigate(`/admin/matches/${m.id}/players`)}
                className="text-green-600"
              >
                Squad
              </button>
              <button
                onClick={() => navigate(`/admin/matches/${m.id}/stats`)}
                className="text-purple-600"
              >
                Stats
              </button>
              <button
                onClick={() => handleCalculate(m.id)}
                className="text-blue-600"
              >
                Calculate
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
