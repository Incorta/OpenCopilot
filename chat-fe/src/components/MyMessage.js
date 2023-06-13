import Grid from '@mui/material/Grid';
import ChatMsg from 'components/ChatMsg/ChatMsg';

const Message = ({ message }) => (
    <Grid item xs={12} container justifyContent="flex-end">
        <ChatMsg
        side={'right'}
        messages={[
            message.text            
        ]}
        />
    </Grid>
);

export default Message;