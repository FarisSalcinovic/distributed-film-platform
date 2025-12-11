export default function Footer() {
  return (
    <footer className="bg-[#0f172a] text-white py-14 px-10 mt-20">
      <div className="max-w-6xl mx-auto">
        
        {/* Top row */}
        <div className="flex flex-col md:flex-row justify-between gap-10">
          
          {/* Left side logo + text */}
          <div>
            <h2 className="text-2xl font-bold mb-3">🎬 CineCity</h2>
            <p className="text-gray-400 text-sm max-w-xs">
              Discover movies in your city, explore trending genres, and track your recent searches.
            </p>

            {/* Social Icons */}
            <div className="flex gap-4 mt-5 text-xl">
              <a href="#" className="hover:text-blue-400">🐦</a>
              <a href="#" className="hover:text-blue-400">📘</a>
              <a href="#" className="hover:text-blue-400">📸</a>
            </div>
          </div>

          {/* Right side links */}
          <div className="flex gap-20">
            
            {/* Product */}
            <div>
              <h3 className="font-semibold mb-3">Product</              h3>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li className="hover:text-white cursor-pointer">Nesto</li>
                <li className="hover:text-white cursor-pointer">Features</li>
                <li className="hover:text-white cursor-pointer">Reviews</li>
              </ul>
            </div>

            {/* Company */}
            <div>
              <h3 className="font-semibold mb-3">Company</h3>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li className="hover:text-white cursor-pointer">About</li>
                <li className="hover:text-white cursor-pointer">Nesto</li>
                <li className="hover:text-white cursor-pointer">Contact</li>
              </ul>
            </div>

          </div>
        </div>

        {/* Divider line */}
        <div className="border-t border-gray-700 mt-10 pt-6 text-gray-500 text-sm flex justify-between">
          <p>© 2025 CineCity. All rights reserved.</p>
          <div className="flex gap-6">
            <p className="hover:text-white cursor-pointer">Privacy Policy</p>
            <p className="hover:text-white cursor-pointer">Terms of Service</p>
          </div>
        </div>

      </div>
    </footer>
  );
}
