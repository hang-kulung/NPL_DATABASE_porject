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

  const getMedalEmoji = (rank: number) => {
    if (rank === 1) return "🥇";
    if (rank === 2) return "🥈";
    if (rank === 3) return "🥉";
    return null;
  };

  return (
    <div className="min-h-screen bg-linear-to-br from-slate-50 via-blue-50/30 to-slate-50 p-8">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@600;700&display=swap');
        
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }
        
        @keyframes shine {
          0% {
            background-position: -200% 0;
          }
          100% {
            background-position: 200% 0;
          }
        }
        
        @keyframes pulse {
          0%, 100% {
            opacity: 1;
          }
          50% {
            opacity: 0.8;
          }
        }
        
        .animate-slide-in {
          animation: slideIn 0.4s ease-out;
        }
        
        .animate-fade-in {
          animation: fadeIn 0.3s ease-out;
        }
        
        .shine-effect {
          background: linear-gradient(
            90deg,
            transparent 0%,
            rgba(255, 255, 255, 0.3) 50%,
            transparent 100%
          );
          background-size: 200% 100%;
          animation: shine 3s infinite;
        }
        
        .rank-badge {
          font-family: 'Space Grotesk', sans-serif;
        }
        
        * {
          font-family: 'Inter', sans-serif;
        }
        
        .top-rank-shadow-1 {
          box-shadow: 0 4px 20px rgba(239, 68, 68, 0.25), 0 0 40px rgba(239, 68, 68, 0.1);
        }
        
        .top-rank-shadow-2 {
          box-shadow: 0 4px 20px rgba(59, 130, 246, 0.25), 0 0 40px rgba(59, 130, 246, 0.1);
        }
        
        .top-rank-shadow-3 {
          box-shadow: 0 4px 20px rgba(148, 163, 184, 0.25), 0 0 40px rgba(148, 163, 184, 0.1);
        }
      `}</style>
      
      <div className="max-w-6xl mx-auto flex gap-6">
        
        {/* Sidebar */}
        <div className="w-72 animate-slide-in">
          <div className="bg-white rounded-2xl shadow-lg border border-slate-200 overflow-hidden">
            
            {/* Filter Header */}
            <div className="relative bg-linear-to-br from-blue-600 via-blue-700 to-blue-800 p-6 overflow-hidden">
              <div className="absolute inset-0 opacity-20 shine-effect"></div>
              <div className="relative z-10">
                <h2 className="text-white font-bold text-xl">Match Filter</h2>
                <p className="text-blue-100 text-sm mt-1">Select a match to view</p>
              </div>
              <div className="absolute -right-8 -top-8 w-32 h-32 bg-white/10 rounded-full blur-2xl"></div>
            </div>

            {/* All Matches Option */}
            <div className="p-5">
              <button
                onClick={() => setSelectedMatch("all")}
                className={`w-full text-left px-5 py-4 rounded-xl transition-all duration-300 ${
                  selectedMatch === "all"
                    ? 'bg-linear-to-r from-red-500 to-red-600 text-white shadow-lg shadow-red-500/30 scale-[1.02]'
                    : 'bg-slate-50 text-slate-700 hover:bg-slate-100 hover:shadow-md'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <span className="font-semibold">All Matches</span>
                    <div className="text-xs mt-0.5 opacity-90">Complete rankings</div>
                  </div>
                  {selectedMatch === "all" && (
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  )}
                </div>
              </button>
            </div>

            {/* Match List */}
            <div className="px-5 pb-5">
              <div className="flex items-center gap-2 mb-4 px-2">
                <div className="h-px flex-1 bg-linear-to-r from-transparent via-slate-300 to-transparent"></div>
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Matches</span>
                <div className="h-px flex-1 bg-linear-to-r from-transparent via-slate-300 to-transparent"></div>
              </div>
              <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
                {matches.map((m) => (
                  <button
                    key={`match-${m.match_id}`}
                    onClick={() => setSelectedMatch(m.match_id)}
                    className={`w-full text-left px-4 py-3.5 rounded-xl transition-all duration-300 ${
                      selectedMatch === m.match_id
                        ? 'bg-linear-to-r from-blue-500 to-blue-600 text-white shadow-lg shadow-blue-500/30 scale-[1.02]'
                        : 'bg-slate-50 text-slate-700 hover:bg-slate-100 hover:shadow-md'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="text-sm font-semibold">{m.team1}</div>
                        <div className="flex items-center gap-1.5 my-1">
                          <div className="h-px flex-1 bg-current opacity-20"></div>
                          <span className="text-[10px] font-bold opacity-60">VS</span>
                          <div className="h-px flex-1 bg-current opacity-20"></div>
                        </div>
                        <div className="text-sm font-semibold">{m.team2}</div>
                      </div>
                      {selectedMatch === m.match_id && (
                        <svg className="w-5 h-5 shrink-0 ml-2" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Leaderboard */}
        <div className="flex-1 animate-slide-in" style={{ animationDelay: '0.1s' }}>
          <div className="bg-white rounded-2xl shadow-lg border border-slate-200 overflow-hidden">
            
            {/* Header */}
            <div className="relative bg-linear-to-r from-slate-900 via-slate-800 to-slate-900 p-8 overflow-hidden">
              <div className="absolute inset-0 opacity-10 shine-effect"></div>
              <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl"></div>
              <div className="absolute bottom-0 left-0 w-64 h-64 bg-red-500/10 rounded-full blur-3xl"></div>
              <div className="relative z-10 flex items-center gap-4">
                <div className="text-5xl drop-shadow-lg">🏆</div>
                <div>
                  <h1 className="text-3xl font-bold text-white">
                    {selectedMatch === "all" ? "Overall Leaderboard" : "Match Leaderboard"}
                  </h1>
                  <p className="text-slate-300 text-sm mt-1">
                    {selectedMatch === "all" 
                      ? "Complete tournament rankings" 
                      : "Individual match standings"}
                  </p>
                </div>
              </div>
            </div>

            {/* Table */}
            <div className="p-6">
              {loading ? (
                <div className="flex flex-col items-center justify-center py-20 animate-fade-in">
                  <div className="relative">
                    <div className="w-16 h-16 border-4 border-slate-200 border-t-blue-600 rounded-full animate-spin"></div>
                  </div>
                  <p className="text-slate-500 mt-4 font-medium">Loading leaderboard...</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full animate-fade-in">
                    <thead>
                      <tr className="border-b-2 border-slate-200">
                        <th className="text-left py-4 px-5 text-slate-700 font-bold text-sm uppercase tracking-wide">Rank</th>
                        <th className="text-left py-4 px-5 text-slate-700 font-bold text-sm uppercase tracking-wide">Player</th>
                        <th className="text-right py-4 px-5 text-slate-700 font-bold text-sm uppercase tracking-wide">Points</th>
                      </tr>
                    </thead>
                    <tbody>
                      {rows.map((row, index) => {
                        const medal = getMedalEmoji(row.rank);
                        const isTopThree = row.rank <= 3;
                        
                        return (
                          <tr 
                            key={row.user_id} 
                            className={`border-b border-slate-100 transition-all duration-300 ${
                              row.rank === 1
                                ? 'bg-linear-to-r from-red-50/80 to-red-50/40 hover:from-red-50 hover:to-red-50/60 top-rank-shadow-1'
                                : row.rank === 2
                                ? 'bg-linear-to-r from-blue-50/80 to-blue-50/40 hover:from-blue-50 hover:to-blue-50/60 top-rank-shadow-2'
                                : row.rank === 3
                                ? 'bg-linear-to-r from-slate-50/80 to-slate-50/40 hover:from-slate-50 hover:to-slate-50/60 top-rank-shadow-3'
                                : 'hover:bg-slate-50'
                            }`}
                          >
                            <td className="py-5 px-5">
                              <div className="flex items-center gap-3">
                                {medal && (
                                  <span className="text-3xl drop-shadow-md">{medal}</span>
                                )}
                                <div className={`rank-badge text-lg font-bold px-3 py-1 rounded-lg ${
                                  row.rank === 1 
                                    ? 'bg-linear-to-br from-red-500 to-red-600 text-white shadow-lg shadow-red-500/30' 
                                    : row.rank === 2
                                    ? 'bg-linear-to-br from-blue-500 to-blue-600 text-white shadow-lg shadow-blue-500/30'
                                    : row.rank === 3
                                    ? 'bg-linear-to-br from-slate-500 to-slate-600 text-white shadow-lg shadow-slate-500/30'
                                    : 'bg-slate-100 text-slate-600'
                                }`}>
                                  #{row.rank}
                                </div>
                              </div>
                            </td>
                            <td className="py-5 px-5">
                              <span className={`text-lg ${
                                isTopThree ? 'font-bold text-slate-900' : 'font-medium text-slate-700'
                              }`}>
                                {row.username}
                              </span>
                            </td>
                            <td className="py-5 px-5 text-right">
                              <div className="inline-flex items-center gap-2">
                                <span className={`text-xl font-bold tabular-nums ${
                                  row.rank === 1
                                    ? 'text-red-600'
                                    : row.rank === 2
                                    ? 'text-blue-600'
                                    : row.rank === 3
                                    ? 'text-slate-700'
                                    : 'text-slate-600'
                                }`}>
                                  {row.total_points.toFixed(2)}
                                </span>
                                {isTopThree && (
                                  <span className={`text-xs font-semibold px-2 py-0.5 rounded ${
                                    row.rank === 1
                                      ? 'bg-red-100 text-red-700'
                                      : row.rank === 2
                                      ? 'bg-blue-100 text-blue-700'
                                      : 'bg-slate-100 text-slate-700'
                                  }`}>
                                    pts
                                  </span>
                                )}
                              </div>
                            </td>
                          </tr>
                        );
                      })}

                      {rows.length === 0 && (
                        <tr>
                          <td colSpan={3} className="py-16 text-center">
                            <div className="flex flex-col items-center gap-3 animate-fade-in">
                              <div className="text-5xl opacity-40">📊</div>
                              <p className="text-slate-400 text-lg">No data available</p>
                            </div>
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}