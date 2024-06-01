class DebugHelper():


    def stringify_4characters_board(squares):
        """１マス４桁"""
        return f"""\
+----+----+----+----+----+----+----+----+----+
│{squares[72]:4}|{squares[63]:4}|{squares[54]:4}|{squares[45]:4}|{squares[36]:4}|{squares[27]:4}|{squares[18]:4}|{squares[9]:4}|{squares[0]:4}|
+----+----+----+----+----+----+----+----+----+
|{squares[73]:4}|{squares[64]:4}|{squares[55]:4}|{squares[46]:4}|{squares[37]:4}|{squares[28]:4}|{squares[19]:4}|{squares[10]:4}|{squares[1]:4}|
+----+----+----+----+----+----+----+----+----+
|{squares[74]:4}|{squares[65]:4}|{squares[56]:4}|{squares[47]:4}|{squares[38]:4}|{squares[29]:4}|{squares[20]:4}|{squares[11]:4}|{squares[2]:4}|
+----+----+----+----+----+----+----+----+----+
|{squares[75]:4}|{squares[66]:4}|{squares[57]:4}|{squares[48]:4}|{squares[39]:4}|{squares[30]:4}|{squares[21]:4}|{squares[12]:4}|{squares[3]:4}|
+----+----+----+----+----+----+----+----+----+
|{squares[76]:4}|{squares[67]:4}|{squares[58]:4}|{squares[49]:4}|{squares[40]:4}|{squares[31]:4}|{squares[22]:4}|{squares[13]:4}|{squares[4]:4}|
+----+----+----+----+----+----+----+----+----+
|{squares[77]:4}|{squares[68]:4}|{squares[59]:4}|{squares[50]:4}|{squares[41]:4}|{squares[32]:4}|{squares[23]:4}|{squares[14]:4}|{squares[5]:4}|
+----+----+----+----+----+----+----+----+----+
|{squares[78]:4}|{squares[69]:4}|{squares[60]:4}|{squares[51]:4}|{squares[42]:4}|{squares[33]:4}|{squares[24]:4}|{squares[15]:4}|{squares[6]:4}|
+----+----+----+----+----+----+----+----+----+
|{squares[79]:4}|{squares[70]:4}|{squares[61]:4}|{squares[52]:4}|{squares[43]:4}|{squares[34]:4}|{squares[25]:4}|{squares[16]:4}|{squares[7]:4}|
+----+----+----+----+----+----+----+----+----+
|{squares[80]:4}|{squares[71]:4}|{squares[62]:4}|{squares[53]:4}|{squares[44]:4}|{squares[35]:4}|{squares[26]:4}|{squares[17]:4}|{squares[8]:4}|
+----+----+----+----+----+----+----+----+----+"""
