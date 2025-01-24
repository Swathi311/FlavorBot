import React, { useState } from 'react';
import { Box, Typography, IconButton, useMediaQuery, Popover } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import EmojiEmotionsIcon from '@mui/icons-material/EmojiEmotions';
import Picker from '@emoji-mart/react';
import data from '@emoji-mart/data';
import axios from 'axios';

const App = () => {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [anchorEl, setAnchorEl] = useState(null); 
  const isMobile = useMediaQuery('(max-width:600px)');

  const handleSend = async () => {
    if (userInput.trim() === "") return;
  
    // Add user input to the messages array
    const newMessage = { text: userInput, sender: "user" };
    setMessages([...messages, newMessage]);
  
    try {
      // Send the userInput to the Flask backend
      const response = await axios.post("http://localhost:8000/process", {
        text: userInput, // Send userInput as part of the POST request
      });
  
      // Get the response from the backend
      const botResponse = response.data.text; // Assuming backend echoes back the query
      const botMessage = {
        text: botResponse,
        sender: "bot",
      };
  
      // Add the bot's response to the chat
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Error processing text:", error);
      const botMessage = {
        text: "Sorry, there was an error processing your request.",
        sender: "bot",
      };
      setMessages((prev) => [...prev, botMessage]);
    }
  
    // Clear the input field
    setUserInput("");
  };
  
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  const handleEmojiSelect = (emoji) => {
    setUserInput((prev) => prev + emoji.native);
    setAnchorEl(null); 
  };

  const handleOpenEmojiDialog = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleCloseEmojiDialog = () => {
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        bgcolor: '#2c2c2c', 
        alignItems: 'center',
        px: isMobile ? 1 : 2,
      }}
    >
      {/* Title Section */}
      <Box
        sx={{
          width: '100%',
          textAlign: 'left',
          p: isMobile ? 1.5 : 2,
          bgcolor: '#2c2c2c', 
        }}
      >
        <Typography
          variant="h6"
          sx={{
            fontWeight: 'bold',
            fontSize: isMobile ? '16px' : '20px',
            color: 'white',
          }}
        >
          FlavorBot
        </Typography>
        <Typography
          variant="body2"
          sx={{
            fontSize: isMobile ? '12px' : '14px',
            color: 'white',
            opacity: 0.9,
          }}
        >
          Your recipe assistant
        </Typography>
      </Box>

      {/* Chat Section */}
      <Box
        sx={{
          flexGrow: 1,
          overflowY: 'auto',
          p: 2,
          border: '1px solid #444', 
          bgcolor: '#3a3a3a', 
          boxShadow: '0px 2px 4px rgba(0,0,0,0.1)',
          width: isMobile ? '95%' : '60%',
          mt: isMobile ? 1 : 2,
          borderRadius: '16px',
        }}
      >
        {messages.map((msg, index) => (
          <Box
            key={index}
            sx={{
              display: 'flex',
              justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start',
              mb: 1.5,
            }}
          >
            <Box
              sx={{
                p: 1.5,
                borderRadius: 2,
                maxWidth: '70%',
                bgcolor: msg.sender === 'user' ? '#7338A0' : '#e0e0e0',
                color: msg.sender === 'user' ? 'white' : 'black',
                boxShadow: msg.sender === 'user' ? '0px 2px 5px rgba(0,0,0,0.2)' : 'none',
              }}
            >
              {msg.text}
            </Box>
          </Box>
        ))}
      </Box>

      {/* Input Section */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          borderRadius: '20px',
          bgcolor: '#f4f4f4', 
          p: 1,
          width: isMobile ? '95%' : '60%',
          mt: isMobile ? 0.5 : 1.5,
          boxShadow: '0px 2px 5px rgba(0,0,0,0.1)',
        }}
      >
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          style={{
            flexGrow: 1,
            border: 'none',
            outline: 'none',
            borderRadius: '20px',
            padding: isMobile ? '8px 12px' : '10px 15px',
            fontSize: isMobile ? '14px' : '16px',
            backgroundColor: '#D3D3D3',
            color: '#464748',
          }}
        />

        {/* Emoji Button (Only for Desktop Screens) */}
        {!isMobile && (
          <IconButton
            sx={{ color: '#ddd', ml: 1 }}
            onClick={handleOpenEmojiDialog}
          >
            <EmojiEmotionsIcon />
          </IconButton>
        )}

        <IconButton sx={{ color: '#ddd', ml: 1 }} onClick={handleSend}>
          <SendIcon />
        </IconButton>
      </Box>

      {/* Emoji Picker Popover */}
      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleCloseEmojiDialog}
        anchorOrigin={{
          vertical: 'top',
          horizontal: 'left',
        }}
        transformOrigin={{
          vertical: 'bottom',
          horizontal: 'left',
        }}
      >
        <Picker data={data} onEmojiSelect={handleEmojiSelect} />
      </Popover>
    </Box>
  );
};

export default App;
//checking branch