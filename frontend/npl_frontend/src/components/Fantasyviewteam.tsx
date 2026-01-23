import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

interface Player {
  player_name: string;
  team_name: string;
  role: string;
  cost: number;
  is_captain: boolean;
  is_vice_captain: boolean;
}

export default function FantasyViewTeam() {
  const { matchId } = useParams();
  const navigate = useNavigate();
  const [players, setPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/fantasy/team/${matchId}/`, {
      credentials: "include",
    })
      .then((res) => res.json())
      .then((data) => setPlayers(data.players))
      .finally(() => setLoading(false));
  }, [matchId]);

  if (loading) return <p className="text-center mt-10">Loading team...</p>;

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">My Fantasy Team</h1>

        <button
          onClick={() => navigate(`/fantasy/select/${matchId}`)}
          className="px-4 py-2 rounded-xl bg-red-600 text-white font-semibold"
        >
          Edit Team
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {players.map((p, idx) => (
          <div key={idx} className="p-5 rounded-2xl shadow bg-white">
            <div className="flex justify-between items-center">
              <h2 className="font-bold text-lg">{p.player_name}</h2>

              <div className="flex gap-2">
                {p.is_captain && (
                  <span className="text-xs bg-red-600 text-white px-2 py-1 rounded-full">
                    C
                  </span>
                )}
                {p.is_vice_captain && (
                  <span className="text-xs bg-blue-600 text-white px-2 py-1 rounded-full">
                    VC
                  </span>
                )}
              </div>
            </div>

            <p className="text-gray-500 text-sm mt-1">
              {p.team_name} · {p.role}
            </p>
            <p className="font-bold mt-2">₹ {p.cost}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
