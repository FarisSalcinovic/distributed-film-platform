export default function RecentSearches() {
  const items = [
    {
      city: "Los Angeles",
      time: "2 hours ago",
      color: "#8b5cf6", // purple
      bg: "rgba(139, 92, 246, 0.15)"
    },
    {
      city: "Barcelona",
      time: "1 day ago",
      color: "#8b5cf6", // purple
      bg: "rgba(139, 92, 246, 0.15)"
    },
    {
      city: "Amsterdam",
      time: "3 days ago",
      color: "#f59e0b", // yellow
      bg: "rgba(245, 158, 11, 0.15)"
    },
  ];

  return (
    <section className="mt-20 px-6">
      <div className="bg-white rounded-3xl shadow-lg m-20 p-10">
        
        {/* Title + View All */}
        <div className="flex justify-between items-center mb-2">
          <h2 className="text-xl font-bold">Your Recent Searches</h2>
          <button className="text-sm text-blue-600 font-medium hover:underline">
            View All
          </button>
        </div>

        {/* Subtitle */}
        <p className="text-gray-500 mb-8">
          Quick access to your previous discoveries
        </p>

        {/* Horizontal cards */}
        <div className="flex gap-8 flex-wrap justify-around">
          {items.map((item, i) => (
            <div
              key={i}
              className="bg-gray-50 rounded-2xl shadow-sm p-6 flex items-center gap-4 w-64 hover:shadow-md transition"
            >
              {/* Icon container */}
              <div
                className="w-10 h-10 rounded-xl flex items-center justify-center"
                style={{ backgroundColor: item.bg }}
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill={item.color}
                  viewBox="0 0 24 24"
                  strokeWidth="1.5"
                  stroke={item.color}
                  className="w-5 h-5"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z"
                  />
                </svg>
              </div>

              {/* Text */}
              <div>
                <p className="font-semibold text-gray-900">{item.city}</p>
                <p className="text-sm text-gray-500">{item.time}</p>
              </div>
            </div>
          ))}
        </div>

      </div>
    </section>
  );
}
