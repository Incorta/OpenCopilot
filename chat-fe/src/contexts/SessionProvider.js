import React, { createContext, useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';

// Create a Context
export const SessionContext = createContext();

// Create a Context Provider
export const SessionProvider = ({ children }) => {
  const [session, setSession] = useState(null);


  useEffect(() => {
    // Generate a UUID and set it as the session when the component first mounts
    const newUuid = uuidv4();
    setSession({
        sessionId: newUuid,
    });
  }, []);

  return (
    <SessionContext.Provider value={{ session }}>
      {children}
    </SessionContext.Provider>
  );
};
