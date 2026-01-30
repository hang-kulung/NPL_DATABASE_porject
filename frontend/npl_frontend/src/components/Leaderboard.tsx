
import { useEffect, useState } from "react";

interface Match {
  match_id: number;
  team1: string;
  team2: string;
}


interface LeaderboardRow {
  rank: number;
  user_id: number;
  username: string;
  total_points: number;
}

export default function OverallLeaderboard() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [selectedMatch, setSelectedMatch] = useState<number | "all">("all");
  const [rows, setRows] = useState<LeaderboardRow[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch matches
  useEffect(() => {
    fetch("http://127.0.0.1:8000/fantasy/matches/")
      .then(res => res.json())
      .then(data => setMatches(data.matches))
      .catch(console.error);
  }, []);

  // Fetch leaderboard
  useEffect(() => {
    setLoading(true);

    const url =
      selectedMatch === "all"
        ? "http://127.0.0.1:8000/leaderboard/api/overall/"
        : `http://127.0.0.1:8000/leaderboard/api/match/${selectedMatch}/`;

    fetch(url)
      .then(res => res.json())
      .then(data => {
        setRows(data.leaderboard);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [selectedMatch]);

  useEffect(() => {
    console.log("Matches loaded:", matches);
  }, [matches]);

  return (
    <div className="max-w-5xl mx-auto p-6 flex gap-6">
      
      {/* Sidebar */}
      <div className="w-64">
        <h2 className="font-semibold mb-2">Filter by Match</h2>

        <select
          value={selectedMatch}
          onChange={(e) => {
            const value = e.target.value;
            setSelectedMatch(value === "all" ? "all" : parseInt(value));
          }}
          className="w-full border p-2 rounded"
        >
          <option value="all">All Matches</option>

          {matches.map((m) => (
            <option key={`match-${m.match_id}`} value={m.match_id}>
              {m.team1} vs {m.team2}
            </option>
          ))}
        </select>

      </div>

      {/* Leaderboard */}
      <div className="flex-1">
        <h1 className="text-2xl font-bold mb-4">
          🏆 {selectedMatch === "all" ? "Overall Leaderboard" : "Match Leaderboard"}
        </h1>

        {loading ? (
          <p>Loading leaderboard...</p>
        ) : (
          <table className="w-full border border-gray-200 rounded-lg overflow-hidden">
            <thead className="bg-gray-100">
              <tr>
                <th className="p-3 text-left">Rank</th>
                <th className="p-3 text-left">User</th>
                <th className="p-3 text-right">Points</th>
              </tr>
            </thead>
            <tbody>
              {rows.map(row => (
                <tr key={row.user_id} className="border-t">
                  <td className="p-3 font-semibold">#{row.rank}</td>
                  <td className="p-3">{row.username}</td>
                  <td className="p-3 text-right font-mono">
                    {row.total_points.toFixed(2)}
                  </td>
                </tr>
              ))}

              {rows.length === 0 && (
                <tr>
                  <td colSpan={3} className="p-4 text-center text-gray-500">
                    No data available
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

