import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

interface Match {
  id: number;
  teams: string;
  time: string;
  status: string;
}

export default function MyTeams() {
  const navigate = useNavigate();
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMatches = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/matches/", {
          credentials: "include",
        });
        if (!res.ok) throw new Error("Failed to fetch matches");

        const data = await res.json();
        setMatches(data.matches ?? data);
      } catch (err: any) {
        setError(err.message || "Something went wrong");
      } finally {
        setLoading(false);
      }
    };

    fetchMatches();
  }, []);

  const handleTeamClick = async (matchId: number) => {
    try {
      const csrfRes = await fetch("http://127.0.0.1:8000/users/csrf/", {
        credentials: "include",
      });

      const csrfToken = document.cookie
        .split("; ")
        .find((row) => row.startsWith("csrftoken="))
        ?.split("=")[1];

      const res = await fetch(
        `http://127.0.0.1:8000/fantasy/create/${matchId}/`,
        {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
            ...(csrfToken && { "X-CSRFToken": csrfToken }),
          },
          body: JSON.stringify({}),
        }
      );

      const data = await res.json();
      // Redirect based on backend response
      if (data.status === "created") {
        navigate(`/fantasy/select/${matchId}`);
      } else if (data.status === "exists") {
        navigate(`/fantasy/view/${matchId}`);
      } else {
        alert("Unexpected server response");
      }
    } catch (err: any) {
      console.error("Error handling team:", err);
      alert(err.message || "Something went wrong");
    }
  };

  if (loading)
    return (
      <p className="text-center text-gray-500 mt-8">Loading matches...</p>
    );

  if (error)
    return <p className="text-center text-red-600 mt-8">{error}</p>;

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <h1 className="text-2xl font-bold mb-6">My Teams</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {matches.map((match) => (
          <div
            key={match.id}
            className="bg-white rounded-xl p-4 shadow-sm flex flex-col justify-between"
          >
            <div>
              <h2 className="font-semibold text-lg">{match.teams}</h2>
              <p className="text-sm text-gray-500 mt-1">{match.time}</p>
            </div>
            <button
              onClick={() => handleTeamClick(match.id)}
              className="mt-4 text-red-600 font-semibold hover:underline self-start"
            >
              View / Edit Team →
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
