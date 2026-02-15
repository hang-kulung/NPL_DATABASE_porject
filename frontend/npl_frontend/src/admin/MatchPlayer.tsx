import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { apiFetch } from "./api";

interface PlayerRow {
  player_id: number;
  player_name: string;
  team_name: string;
  is_playing: boolean;
}

interface MatchInfo {
  id: number;
  date: string;
  team1_name: string;
  team2_name: string;
}

export default function AdminMatchPlayers() {
  const { matchId } = useParams();
  const [players, setPlayers] = useState<PlayerRow[]>([]);
  const [match, setMatch] = useState<MatchInfo | null>(null);
  const [selected, setSelected] = useState<Set<number>>(new Set());

  const  navigate = useNavigate();
  const load = async () => {
    const res = await apiFetch(`match_players/${matchId}/`);
    setPlayers(res.players);
    setMatch(res.match);

    const playing = new Set<number>();
    res.players.forEach((p: PlayerRow) => {
      if (p.is_playing) playing.add(p.player_id);
    });
    setSelected(playing);
  };

  useEffect(() => {
    load();
  }, [matchId]);

  const toggle = (id: number) => {
    const copy = new Set(selected);
    copy.has(id) ? copy.delete(id) : copy.add(id);
    setSelected(copy);
  };

  const save = async () => {
    await apiFetch(`match_players/${matchId}/update/`, {
      method: "POST",
      body: JSON.stringify({
        playing_ids: Array.from(selected),
      }),
    });
    alert("Squad updated");
    navigate(`/admin/matches/`);
  };

  if (!match) return <p>Loading...</p>;

  return (
    <div className="max-w-3xl mx-auto">
      <h2 className="text-xl font-bold mb-4">
        Squad — {match.team1_name} vs {match.team2_name}
      </h2>

      <table className="w-full border">
        <thead>
          <tr className="bg-gray-100">
            <th className="p-2">Player</th>
            <th>Team</th>
            <th>Playing</th>
          </tr>
        </thead>

        <tbody>
          {players.map(p => (
            <tr key={p.player_id} className="border-t">
              <td className="p-2">{p.player_name}</td>
              <td>{p.team_name}</td>
              <td className="text-center">
                <input
                  type="checkbox"
                  checked={selected.has(p.player_id)}
                  onChange={() => toggle(p.player_id)}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <button
        onClick={save}
        className="mt-4 bg-red-600 text-white px-4 py-2 rounded"
      >
        Save Squad
      </button>
    </div>
  );
}
