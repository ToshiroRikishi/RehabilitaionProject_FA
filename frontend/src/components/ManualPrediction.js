import React, { useState } from 'react';
import axios from 'axios';

const ManualPrediction = () => {
  const [formData, setFormData] = useState({
    dynamometry: '',
    feet_together: '',
    walk_4m: '',
    barthel_score: '',
  });
  const [result, setResult] = useState(null);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:8000/api/predict-activity-manual', formData);
      setResult(response.data);
    } catch (error) {
      console.error('Error predicting activity:', error);
      setResult({ message: 'Error predicting activity', activity_level: '' });
    }
  };

  return (
    <div className="border p-4 rounded">
      <h2 className="text-xl font-semibold mb-2">Manual Prediction</h2>
      <form onSubmit={handleSubmit} className="space-y-2">
        <input
          type="number"
          name="dynamometry"
          placeholder="Dynamometry (kg)"
          value={formData.dynamometry}
          onChange={handleChange}
          className="border p-2 w-full"
          step="0.1"
        />
        <input
          type="number"
          name="feet_together"
          placeholder="Feet Together (seconds)"
          value={formData.feet_together}
          onChange={handleChange}
          className="border p-2 w-full"
          step="0.1"
        />
        <input
          type="number"
          name="walk_4m"
          placeholder="4m Walk (seconds)"
          value={formData.walk_4m}
          onChange={handleChange}
          className="border p-2 w-full"
          step="0.1"
        />
        <input
          type="number"
          name="barthel_score"
          placeholder="Barthel Score"
          value={formData.barthel_score}
          onChange={handleChange}
          className="border p-2 w-full"
        />
        <button type="submit" className="bg-blue-500 text-white p-2 rounded">
          Predict
        </button>
      </form>
      {result && (
        <div className="mt-2">
          <p>{result.message}</p>
          <p>Activity Level: {result.activity_level}</p>
        </div>
      )}
    </div>
  );
};

export default ManualPrediction;