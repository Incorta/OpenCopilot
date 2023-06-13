import React, { useState, useEffect, useRef } from 'react';
import { Grid, TextField, Paper } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({
    rootWindow: {
        height: '80vh'
    },
    chatContainer: {   
        overflow: 'auto',
        maxHeight: '70vh'
    },
    chatMessagesPaper: {
        height: '100%', padding: '20px'
    },
    chatInput: {
      position: 'fixed',
      bottom: 0,
      width: '100%',
    },
  }));  

const ChatWindow = () => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");

  const classes = useStyles();

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleNewMessageChange = (event) => {
    setNewMessage(event.target.value);
  };

  const handleSendMessage = (event) => {
    event.preventDefault();

    if(newMessage !== "") {
      setMessages([...messages, newMessage]);
      setNewMessage("");
    }
  };

  return (
    <Grid container direction="column" justify="space-between" className={classes.rootWindow}>
      <Grid item className={classes.chatContainer}>
        <Paper className={classes.chatMessagesPaper}>
          {messages.map((message, i) => (
            <div key={i}>
              {message}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </Paper>
      </Grid>
      <Grid item>
        <form onSubmit={handleSendMessage}>
          <TextField
            value={newMessage}
            onChange={handleNewMessageChange}
            placeholder="Type a message..."
            fullWidth
            variant="outlined"
          />
        </form>
      </Grid>
    </Grid>
  );
};

export default ChatWindow;
