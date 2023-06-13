import React, { useState, useEffect, useRef } from 'react';
import { Grid, Paper } from '@material-ui/core';
import { v4 as uuidv4 } from 'uuid';
import { makeStyles } from '@material-ui/core/styles';

import ActiveMessage from 'components/ActiveMessage';
import MyMessage from 'components/MyMessage';
import RobotMessage from 'components/RobotReply/RobotMessage';
import ChatInput from 'components/ChatInput';

const useStyles = makeStyles((theme) => ({
  rootWindow: {
    minHeight: '100vh',
    paddingLeft: '50px',
    paddingRight: '50px',
  },
  chatContainer: {   
      overflow: 'auto',
      maxHeight: '80vh',
      minHeight: '80vh',
      overflowX: "hidden",
      paddingTop: "20px"
  },
  chatMessagesPaper: {
      height: '100%', padding: '20px'
  }
}));

/*
const DefaultChatMsg = () => (
  <Grid container direction="column" style={{width: "70%"}}>
    <Grid item xs={12} container justifyContent="flex-start">
      <ChatMsg
        avatar={BsRobot}
        messages={[
          'Hi Jenny, How r u today?',
          'Did you train yesterday',
          'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Volutpat lacus laoreet non curabitur gravida.',
        ]}
      />
    </Grid>
    <Grid item xs={12} justifyContent="flex-start" flexDirection="column">
      <LeftAlignedMessageWrapper>
        <LineChart />
      </LeftAlignedMessageWrapper>
    </Grid>
    <Grid item xs={12} container justifyContent="flex-end">
      <ChatMsg
        side={'right'}
        messages={[
          "Great! What's about you?",
          'Of course I did. Speaking of which check this out',
        ]}
      />
    </Grid>
    <Grid item xs={12} container justifyContent="flex-start">
      <ChatMsg avatar={BsRobot} messages={['Im good.', 'See u later.']} />
    </Grid>
  </Grid>
);

export default DefaultChatMsg;

*/

const ChatWindow = () => {
  const [messages, setMessages] = useState([]);
  const classes = useStyles();

  const handleMessageSubmit = (text) => {
    // replace with function to send message to server
    const myMessage = { id: uuidv4(), time: Date.now(), text: text, myMessage: true, final: true };
    const robotMessage = { id: uuidv4(), time: Date.now(), text: text, myMessage: false, final: false };
    setMessages((msgs) => [...msgs, myMessage, robotMessage]);
  };

  const handleMessageFinish = (allUiCommands, activeMessage) => {
    const newMessages = allUiCommands.map(uiCommand => ({
      id: uuidv4(),
      time: Date.now(),
      text: "...",
      myMessage: false,
      final: true,
      uiCommand: uiCommand
    }));    

    setMessages((msgs) => {
      const allCurrMessages = [
        ...msgs.filter(msg => msg.id != activeMessage.id),
        ...newMessages
      ];

      console.log("All current messages", allCurrMessages);

      return allCurrMessages;
    });
  };

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);


  return (
      <Grid container direction="column" justify="space-between" className={classes.rootWindow} >
        <Grid item xs={12} className={classes.chatContainer}>
          {messages.map((message) =>
            message.myMessage ? (
              <MyMessage key={message.id} message={message} />
            ) : !message?.final ? (
                <ActiveMessage
                  key={message.id}
                  message={message}
                  onFinish={handleMessageFinish}
                />
              ) : (
                <RobotMessage key={message.id} message={message} />
              )
          )}
          <div style={{height: "100px"}} />
          <div ref={messagesEndRef} />          
        </Grid>
        <Grid item xs={12}>
          <ChatInput onSubmit={handleMessageSubmit} />
        </Grid>
        <div style={{height: "10px"}} />
      </Grid>      
  );
};

export default ChatWindow;