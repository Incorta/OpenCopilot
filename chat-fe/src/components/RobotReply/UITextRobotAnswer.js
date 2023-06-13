import ChatMsg from 'components/ChatMsg/ChatMsg';
import Grid from '@mui/material/Grid';

const Message = ({ data }) => (
    <Grid item xs={12} container justifyContent="flex-start">
      <ChatMsg
        messages={[
          data.result.message
        ]}
      />
    </Grid>   
);

export default Message;