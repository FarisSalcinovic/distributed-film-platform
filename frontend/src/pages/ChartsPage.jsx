// frontend/src/pages/ChartsPage.jsx
import React from 'react';
import MainNavbar from '../components/MainNavbar';
import Footer from '../components/Footer';

const ChartsPage = () => {
  return (
    <>
      <MainNavbar />
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-4">Grafička Analitika Filmova</h1>
        <p className="text-gray-600 mb-8">Pregledajte statističke podatke o filmovima kroz interaktivne grafikone.</p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">

          {/* Chart 1 - Placeholder */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-bold mb-4 text-blue-600">Popularnost Žanrova</h2>
            <div className="h-64 bg-gray-100 rounded flex items-center justify-center">
              <div className="text-center">
                <div className="text-4xl mb-2">📊</div>
                <p className="font-semibold">Chart.js Grafik</p>
                <p className="text-sm text-gray-500 mt-2">Instaliraj chart.js za prikaz</p>
              </div>
            </div>
            <div className="mt-4 p-3 bg-blue-50 rounded text-sm">
              <code className="bg-gray-800 text-white p-2 rounded block">
                npm install chart.js react-chartjs-2
              </code>
            </div>
          </div>

          {/* Chart 2 - Placeholder */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-bold mb-4 text-green-600">Ocjene Filmova</h2>
            <div className="h-64 bg-gray-100 rounded flex items-center justify-center">
              <div className="text-center">
                <div className="text-4xl mb-2">⭐</div>
                <p className="font-semibold">Distribucija Ocjena</p>
                <p className="text-sm text-gray-500 mt-2">Chart.js će prikazati podatke</p>
              </div>
            </div>
            <div className="mt-4">
              <button
                className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded"
                onClick={() => alert('Instaliraj Chart.js prvo!')}
              >
                Instaliraj Chart.js
              </button>
            </div>
          </div>

          {/* Chart 3 - Full width */}
          <div className="md:col-span-2 bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-bold mb-4 text-purple-600">Filmovi po Godinama</h2>
            <div className="h-80 bg-gray-100 rounded flex items-center justify-center">
              <div className="text-center">
                <div className="text-4xl mb-2">📈</div>
                <p className="font-semibold">Linijski Grafikon</p>
                <p className="text-sm text-gray-500 mt-2">Prikaz trendova kroz godine</p>
              </div>
            </div>
            <div className="mt-4 p-4 bg-purple-50 rounded">
              <h3 className="font-bold mb-2">Koraci za instalaciju:</h3>
              <ol className="list-decimal pl-5 space-y-1">
                <li>Otvori terminal u frontend folderu</li>
                <li>Pokreni: <code className="bg-gray-800 text-white px-2 py-1 rounded text-sm">npm install chart.js react-chartjs-2</code></li>
                <li>Restartuj aplikaciju: <code className="bg-gray-800 text-white px-2 py-1 rounded text-sm">npm start</code></li>
              </ol>
            </div>
          </div>

        </div>

        {/* Quick Stats */}
        <div className="mt-12">
          <h2 className="text-2xl font-bold mb-6">Brze Statistike</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">1,247</div>
              <div className="text-sm text-gray-600">Ukupno Filmova</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-green-600">7.8</div>
              <div className="text-sm text-gray-600">Prosječna Ocjena</div>
            </div>
            <div className="bg-yellow-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">24</div>
              <div className="text-sm text-gray-600">Zemlje</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">15</div>
              <div className="text-sm text-gray-600">Žanrova</div>
            </div>
          </div>
        </div>

      </div>
      <Footer />
    </>
  );
};

export default ChartsPage;