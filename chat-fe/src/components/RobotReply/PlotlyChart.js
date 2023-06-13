import React from 'react';
import Plot from 'react-plotly.js';
import Box from '@mui/material/Box';

const PlotlyChart = ({ data , layout }) => {
  return (
    <Box display="inline-flex">
      <Plot
        data={data}
        layout={layout}
      />
    </Box>
  );
}

export default PlotlyChart;
