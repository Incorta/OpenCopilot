import ChatMsg from 'components/ChatMsg/ChatMsg';
import Grid from '@mui/material/Grid';
import PlotlyChart from 'components/RobotReply/PlotlyChart'
import LeftAlignedMessageWrapper from './LeftAlignedMessageWrapper';

const Message = ({ data }) => {
  var chartJSON = JSON.parse(data.result);
  var chartData = ""
  if ("data" in chartJSON) {
    chartData = chartJSON.data;
  }
  var chartLayout = ""
  if ("layout" in chartJSON) {
    chartLayout = chartJSON.layout;
  }

  return (
    <Grid item xs={12} justifyContent="flex-start" flexDirection="column">
      <LeftAlignedMessageWrapper>
        <PlotlyChart data={chartData} layout={chartLayout} />
      </LeftAlignedMessageWrapper>
    </Grid>
  )  
};

export default Message;