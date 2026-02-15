import { useEffect, useState } from "react";
import { apiFetch } from "./api";

interface Player {
  player_id: string;
  player_name: string;
  role: string;
  cost: number;
  team_id: number;
  team_name: string;
}

interface Team {
  team_id: number;
  team_name: string;
}

export default function Players() {
  const [players, setPlayers] = useState<Player[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);

  const [filterPlayerId, setFilterPlayerId] = useState("");
  const [filterName, setFilterName] = useState("");
  const [filterRole, setFilterRole] = useState("");
  const [filterTeam, setFilterTeam] = useState(0);
  const [filterMaxCost, setFilterMaxCost] = useState("");

  const [editingId, setEditingId] = useState<string | null>(null);
  const [playerId, setPlayerId] = useState("");
  const [name, setName] = useState("");
  const [role, setRole] = useState("");
  const [cost, setCost] = useState(0);
  const [teamId, setTeamId] = useState(0);

  const fetchTeams = async () => {
    const res = await apiFetch("teams/");
    setTeams(res.teams);
    if (res.teams.length) setTeamId(res.teams[0].team_id);
  };

  const fetchPlayers = async (filters: any = {}) => {
    let url = "players/";
    const params = new URLSearchParams();
    for (const key in filters) {
      if (filters[key]) params.append(key, filters[key]);
    }
    if ([...params].length) url += "?" + params.toString();

    const res = await apiFetch(url);
    setPlayers(res.players);
  };

  useEffect(() => {
    fetchTeams();
    fetchPlayers();
  }, []);

  const handleFilter = () => {
    fetchPlayers({
      player_id: filterPlayerId,
      name: filterName,
      role: filterRole,
      team_id: filterTeam || "",
      max_cost: filterMaxCost
    });
  };

  const resetForm = () => {
    setEditingId(null);
    setPlayerId("");
    setName("");
    setRole("");
    setCost(0);
  };

  const isFormValid = () => {
  return (
    playerId.trim() !== "" &&
    name.trim() !== "" &&
    role !== "" &&
    cost > 0 &&
    teamId !== 0
    );
  };


  const handleAdd = async () => {
    if (!isFormValid()) {
      alert("Please fill all fields");
      return;
    }
    await apiFetch("players/add/", {
      method: "POST",
      body: JSON.stringify({
        player_id: playerId,
        player_name: name,
        role,
        cost,
        team_id: teamId,
      }),
    });
    resetForm();
    fetchPlayers();
  };

  const handleUpdate = async () => {
    if (!editingId) return;

    if (!name.trim() || !role || cost <= 0 || teamId === 0) {
      alert("Please fill all fields");
      return;
    }

    await apiFetch(`players/${editingId}/edit/`, {
      method: "PUT",
      body: JSON.stringify({
        player_name: name,
        role,
        cost,
        team_id: teamId,
      }),
    });

    resetForm();
    fetchPlayers();
  };

  const handleDelete = async (id: string) => {
    await apiFetch(`players/${id}/delete/`, { method: "DELETE" });
    fetchPlayers();
  };

  const handleEdit = (p: Player) => {
    setEditingId(p.player_id);
    setPlayerId(p.player_id);
    setName(p.player_name);
    setRole(p.role);
    setCost(p.cost);
    setTeamId(p.team_id);
  };

  const roles = ["BOWLER", "BATTER", "ALLROUNDER"];


  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Players</h2>

      {/* --- FILTER SECTION --- */}
      <div className="flex gap-2 mb-4">
        <input
            placeholder="Player ID"
            value={filterPlayerId}
            onChange={(e) => setFilterPlayerId(e.target.value)}
            className="border px-2 py-1 rounded"
          />
        <input
          placeholder="Name"
          value={filterName}
          onChange={(e) => setFilterName(e.target.value)}
          className="border px-2 py-1 rounded"
        />
        <select
          value={filterRole}
          onChange={(e) => setFilterRole(e.target.value)}
          className="border px-2 py-1 rounded"
        >
          <option value="">All Roles</option>
          {roles.map((role) => (
            <option key={role} value={role}>
              {role}
            </option>
          ))}
        </select>


        <select
          value={filterTeam}
          onChange={(e) => setFilterTeam(+e.target.value)}
          className="border px-2 py-1 rounded"
        >
          <option value={0}>All Teams</option>
          {teams.map((t) => (
            <option key={t.team_id} value={t.team_id}>
              {t.team_name}
            </option>
          ))}
        </select>
        <input
          type="number"
          placeholder="Max Cost"
          value={filterMaxCost}
          onChange={(e) => setFilterMaxCost(e.target.value)}
          className="border px-2 py-1 rounded"
        />
        <button onClick={handleFilter} className="bg-blue-600 text-white px-4 py-1 rounded">
          Filter
        </button>
      </div>

      {/* --- ADD / EDIT FORM --- */}
      <div className="flex gap-2 mb-4">
        {!editingId && (
          <input required
            placeholder="Player ID"
            value={playerId}
            onChange={(e) => setPlayerId(e.target.value)}
            className="border px-2 py-1 rounded"
          />
        )}

        <input required
          placeholder="Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="border px-2 py-1 rounded"
        />
        <select required
          value={role}
          onChange={(e) => setRole(e.target.value)}
          className="border px-2 py-1 rounded"
        >
          <option value="">Select Role</option>
          {roles.map((role) => (
            <option key={role} value={role}>
              {role}
            </option>
          ))}
        </select>
        <input required
          type="number"
          placeholder="Cost"
          value={cost}
          onChange={(e) => setCost(+e.target.value)}
          className="border px-2 py-1 rounded"
        />
        <select required
          value={teamId}
          onChange={(e) => setTeamId(+e.target.value)}
          className="border px-2 py-1 rounded"
        >
          {teams.map((t) => (
            <option key={t.team_id} value={t.team_id}>
              {t.team_name}
            </option>
          ))}
        </select>

        {/* <button
          onClick={editingId ? handleUpdate : handleAdd}
          className="bg-green-600 text-white px-4 py-1 rounded"
        >
          {editingId ? "Update" : "Add"}
        </button> */}
          <button
          onClick={editingId ? handleUpdate : handleAdd}
          disabled={!isFormValid()}
          className={`px-4 py-1 rounded text-white ${
            isFormValid() ? "bg-green-600" : "bg-gray-400 cursor-not-allowed"
          }`}
        >
          {editingId ? "Update" : "Add"}
        </button>

        {editingId && (
          <button onClick={resetForm} className="border px-3 py-1 rounded">
            Cancel
          </button>
        )}
      </div>

      {/* --- PLAYERS LIST --- */}
      <ul className="space-y-2">
        {players.map((p) => (
          <li
            key={p.player_id}
            className="flex justify-between bg-gray-100 p-2 rounded"
          >
            <span>
              {p.player_name} ({p.role}) — {p.team_name} — Cost {p.cost}
            </span>

            <div className="flex gap-3">
              <button
                onClick={() => handleEdit(p)}
                className="text-blue-600"
              >
                Edit
              </button>
              <button
                onClick={() => handleDelete(p.player_id)}
                className="text-red-600"
              >
                Delete
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
