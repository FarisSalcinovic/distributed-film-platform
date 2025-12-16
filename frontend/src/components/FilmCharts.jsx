// frontend/src/components/FilmCharts.jsx
import React, { useState, useEffect } from 'react';
import SimpleChart from './SimpleChart';
import { analyticsAPI } from '../services/etlApi';

const FilmCharts = () => {
  const [chartsData, setChartsData] = useState({
    ratings: null,
    genres: null,
    yearly: null
  });

  useEffect(() => {
    loadChartData();
  }, []);

  const loadChartData = async () => {
    // Mock podaci za sada - kasnije zamijeni sa pravim API pozivima
    const ratingsData = {
      labels: ['1★', '2★', '3★', '4★', '5★', '6★', '7★', '8★', '9★', '10★'],
      datasets: [
        {
          label: 'Broj filmova',
          data: [12, 19, 8, 15, 22, 33, 45, 67, 54, 32],
          backgroundColor: 'rgba(54, 162, 235, 0.6)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1,
        },
      ],
    };

    const genresData = {
      labels: ['Akcija', 'Drama', 'Komedija', 'Horor', 'Romantika', 'Sci-Fi', 'Triler'],
      datasets: [
        {
          label: 'Popularnost žanrova',
          data: [65, 59, 80, 81, 56, 55, 40],
          backgroundColor: [
            'rgba(255, 99, 132, 0.6)',
            'rgba(54, 162, 235, 0.6)',
            'rgba(255, 206, 86, 0.6)',
            'rgba(75, 192, 192, 0.6)',
            'rgba(153, 102, 255, 0.6)',
            'rgba(255, 159, 64, 0.6)',
            'rgba(199, 199, 199, 0.6)',
          ],
          borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64, 1)',
            'rgba(199, 199, 199, 1)',
          ],
          borderWidth: 1,
        },
      ],
    };

    const yearlyData = {
      labels: ['2019', '2020', '2021', '2022', '2023', '2024'],
      datasets: [
        {
          label: 'Filmovi po godini',
          data: [65, 59, 80, 81, 56, 55],
          fill: false,
          borderColor: 'rgb(75, 192, 192)',
          tension: 0.1,
        },
      ],
    };

    setChartsData({
      ratings: ratingsData,
      genres: genresData,
      yearly: yearlyData
    });
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 p-4">
      <div>
        <h3 className="text-lg font-bold mb-4">Distribucija ocjena filmova</h3>
        {chartsData.ratings && (
          <SimpleChart
            type="bar"
            title="Ocjene filmova"
            data={chartsData.ratings}
            options={{
              scales: {
                y: {
                  beginAtZero: true,
                  title: {
                    display: true,
                    text: 'Broj filmova'
                  }
                },
                x: {
                  title: {
                    display: true,
                    text: 'Ocjena'
                  }
                }
              }
            }}
          />
        )}
      </div>

      <div>
        <h3 className="text-lg font-bold mb-4">Popularnost žanrova</h3>
        {chartsData.genres && (
          <SimpleChart
            type="doughnut"
            title="Žanrovi filmova"
            data={chartsData.genres}
          />
        )}
      </div>

      <div className="lg:col-span-2">
        <h3 className="text-lg font-bold mb-4">Filmovi po godinama</h3>
        {chartsData.yearly && (
          <SimpleChart
            type="line"
            title="Broj filmova po godinama"
            data={chartsData.yearly}
            options={{
              scales: {
                y: {
                  beginAtZero: true,
                  title: {
                    display: true,
                    text: 'Broj filmova'
                  }
                },
                x: {
                  title: {
                    display: true,
                    text: 'Godina'
                  }
                }
              }
            }}
          />
        )}
      </div>
    </div>
  );
};

export default FilmCharts;