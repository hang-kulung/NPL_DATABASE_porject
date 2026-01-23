import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getCSRF, getCookie } from "./csrf";

interface Player {
  player_id: number;
  player_name: string;
  role: string;
  cost: number;
  team_name: string;
  team_id: number;
}

export default function FantasySelectPlayers() {
  const { matchId } = useParams();
  const navigate = useNavigate();

  const [players, setPlayers] = useState<Player[]>([]);
  const [selected, setSelected] = useState<number[]>([]);
  const [captain, setCaptain] = useState<number | null>(null);
  const [viceCaptain, setViceCaptain] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const MAX_PLAYERS = 7;
  const MAX_BUDGET = 60;
  const MAX_PER_TEAM = 4;
  const MAX_PER_ROLE = 3;

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/fantasy/select/${matchId}/`, {
      credentials: "include",
    })
      .then((res) => res.json())
      .then((data) => {
        setPlayers(data.players);
        if (data.existing_team) {
    setSelected(data.existing_team.players);
    setCaptain(data.existing_team.captain);
    setViceCaptain(data.existing_team.vice_captain);
        }
      });
      
  }, [matchId]);

  const selectedPlayers = useMemo(
    () => players.filter((p) => selected.includes(p.player_id)),
    [players, selected],
  );

  const totalCost = selectedPlayers.reduce((s, p) => s + p.cost, 0);
  const budgetLeft = MAX_BUDGET - totalCost;
  const playersLeft = MAX_PLAYERS - selected.length;

  const teamCount = useMemo(() => {
    const map: Record<number, number> = {};
    selectedPlayers.forEach((p) => {
      map[p.team_id] = (map[p.team_id] || 0) + 1;
    });
    return map;
  }, [selectedPlayers]);

  const roleCount = useMemo(() => {
    const map: Record<string, number> = {};
    selectedPlayers.forEach((p) => {
      map[p.role] = (map[p.role] || 0) + 1;
    });
    return map;
  }, [selectedPlayers]);

  const togglePlayer = (id: number) => {
    setError(null);

    // remove
    if (selected.includes(id)) {
      setSelected(selected.filter((x) => x !== id));
      if (captain === id) setCaptain(null);
      if (viceCaptain === id) setViceCaptain(null);
      return;
    }

    const p = players.find((x) => x.player_id === id);
    if (!p) return;

    if (selected.length >= MAX_PLAYERS)
      return setError("You can select only 7 players");

    if (budgetLeft < p.cost) return setError("Not enough budget");

    if ((teamCount[p.team_id] || 0) >= MAX_PER_TEAM)
      return setError("Max 4 players allowed from one team");

    if ((roleCount[p.role] || 0) >= MAX_PER_ROLE)
      return setError(`Max 3 players allowed for role: ${p.role}`);

    setSelected([...selected, id]);
  };

  const submitTeam = async () => {
    if (selected.length !== 7) return setError("Select exactly 7 players");

    if (!captain || !viceCaptain)
      return setError("Assign Captain and Vice-Captain");

    if (captain === viceCaptain)
      return setError("Captain and Vice-Captain must be different");

    await getCSRF();
    const csrfToken = getCookie("csrftoken");

    const res = await fetch(
      `http://127.0.0.1:8000/fantasy/select/${matchId}/`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(csrfToken && { "X-CSRFToken": csrfToken }),
        },
        credentials: "include",
        body: JSON.stringify({
          players: selected,
          captain,
          vice_captain: viceCaptain,
        }),
      },
    );

    if (res.ok) navigate(`/fantasy/view/${matchId}`);
    else setError("Failed to save team");
  };

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* PLAYER POOL */}
      <div className="lg:col-span-2">
        <h2 className="text-xl font-bold mb-3">Available Players</h2>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          {players.map((p) => {
            const isSelected = selected.includes(p.player_id);

            return (
              <div
                key={p.player_id}
                onClick={() => togglePlayer(p.player_id)}
                className={`p-3 rounded-xl border cursor-pointer text-sm
                  ${
                    isSelected
                      ? "bg-red-50 border-red-500"
                      : "bg-white hover:bg-gray-50"
                  }`}
              >
                <p className="font-semibold truncate">{p.player_name}</p>
                <p className="text-xs text-gray-500">{p.team_name}</p>
                <p className="text-xs">{p.role}</p>
                <p className="font-bold mt-1">₹{p.cost}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* SELECTED TEAM */}
      {/* SELECTED TEAM */}
      <div className="sticky top-6 h-fit bg-white rounded-2xl shadow-lg p-5">
        <h2 className="text-xl font-bold mb-4">Your Team</h2>

        <div className="flex justify-between text-sm mb-2">
          <span>Players Left</span>
          <span className="font-bold">{playersLeft}</span>
        </div>

        <div className="flex justify-between text-sm mb-4">
          <span>Budget Left</span>
          <span className="font-bold">₹{budgetLeft}</span>
        </div>

        {/* SELECTED PLAYERS */}
        <div className="space-y-2 mb-4">
          {selectedPlayers.map((p) => (
            <div
              key={p.player_id}
              className="flex justify-between items-center bg-gray-50 px-3 py-2 rounded-lg text-sm"
            >
              <span className="truncate">{p.player_name}</span>

              <div className="flex gap-1">
                <button
                  onClick={() => setCaptain(p.player_id)}
                  className={`px-2 py-0.5 rounded text-xs ${
                    captain === p.player_id
                      ? "bg-red-600 text-white"
                      : "bg-gray-200"
                  }`}
                >
                  C
                </button>

                <button
                  onClick={() => setViceCaptain(p.player_id)}
                  className={`px-2 py-0.5 rounded text-xs ${
                    viceCaptain === p.player_id
                      ? "bg-blue-600 text-white"
                      : "bg-gray-200"
                  }`}
                >
                  VC
                </button>
              </div>
            </div>
          ))}

          {/* EMPTY SLOTS */}
          {[...Array(playersLeft)].map((_, i) => (
            <div
              key={i}
              className="text-center text-xs text-gray-400 border border-dashed py-2 rounded-lg"
            >
              Empty Slot
            </div>
          ))}
        </div>

        {error && (
          <p className="text-sm text-red-600 font-semibold mb-3">{error}</p>
        )}

        <button
          onClick={submitTeam}
          className="w-full py-3 rounded-xl hover:bg-red-800 cursor-pointer bg-red-600 text-white font-bold"
        >
          Save Team
        </button>
      </div>
    </div>
  );
}
