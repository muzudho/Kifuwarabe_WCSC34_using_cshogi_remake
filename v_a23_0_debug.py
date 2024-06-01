class DebugHelper():
    """デバッグの助けに使う"""


    def stringify_3characters_board(squares):
        """１マスに３桁を表示できる表

        Parameters
        ----------
        squares : [81]
            ８１マスの表
        """

        return f"""+---+---+---+---+---+---+---+---+---+
|{squares[72]:3}|{squares[63]:3}|{squares[54]:3}|{squares[45]:3}|{squares[36]:3}|{squares[27]:3}|{squares[18]:3}|{squares[9]:3}|{squares[0]:3}|
+---+---+---+---+---+---+---+---+---+
|{squares[73]:3}|{squares[64]:3}|{squares[55]:3}|{squares[46]:3}|{squares[37]:3}|{squares[28]:3}|{squares[19]:3}|{squares[10]:3}|{squares[1]:3}|
+---+---+---+---+---+---+---+---+---+
|{squares[74]:3}|{squares[65]:3}|{squares[56]:3}|{squares[47]:3}|{squares[38]:3}|{squares[29]:3}|{squares[20]:3}|{squares[11]:3}|{squares[2]:3}|
+---+---+---+---+---+---+---+---+---+
|{squares[75]:3}|{squares[66]:3}|{squares[57]:3}|{squares[48]:3}|{squares[39]:3}|{squares[30]:3}|{squares[21]:3}|{squares[12]:3}|{squares[3]:3}|
+---+---+---+---+---+---+---+---+---+
|{squares[76]:3}|{squares[67]:3}|{squares[58]:3}|{squares[49]:3}|{squares[40]:3}|{squares[31]:3}|{squares[22]:3}|{squares[13]:3}|{squares[4]:3}|
+---+---+---+---+---+---+---+---+---+
|{squares[77]:3}|{squares[68]:3}|{squares[59]:3}|{squares[50]:3}|{squares[41]:3}|{squares[32]:3}|{squares[23]:3}|{squares[14]:3}|{squares[5]:3}|
+---+---+---+---+---+---+---+---+---+
|{squares[78]:3}|{squares[69]:3}|{squares[60]:3}|{squares[51]:3}|{squares[42]:3}|{squares[33]:3}|{squares[24]:3}|{squares[15]:3}|{squares[6]:3}|
+---+---+---+---+---+---+---+---+---+
|{squares[79]:3}|{squares[70]:3}|{squares[61]:3}|{squares[52]:3}|{squares[43]:3}|{squares[34]:3}|{squares[25]:3}|{squares[16]:3}|{squares[7]:3}|
+---+---+---+---+---+---+---+---+---+
|{squares[80]:3}|{squares[71]:3}|{squares[62]:3}|{squares[53]:3}|{squares[44]:3}|{squares[35]:3}|{squares[26]:3}|{squares[17]:3}|{squares[8]:3}|
+---+---+---+---+---+---+---+---+---+
"""


    def stringify_double_3characters_boards(left, right):
        """１マスに３桁を表示できる表を２つ並べる

        Parameters
        ----------
        left : [81]
            左側の表
        right : [81]
            右側の表
        """
        return f"""+---+---+---+---+---+---+---+---+---+   +---+---+---+---+---+---+---+---+---+
|{left[72]:3}|{left[63]:3}|{left[54]:3}|{left[45]:3}|{left[36]:3}|{left[27]:3}|{left[18]:3}|{left[9]:3}|{left[0]:3}|   │{right[72]:3}|{right[63]:3}|{right[54]:3}|{right[45]:3}|{right[36]:3}|{right[27]:3}|{right[18]:3}|{right[9]:3}|{right[0]:3}|
+---+---+---+---+---+---+---+---+---+   +---+---+---+---+---+---+---+---+---+
|{left[73]:3}|{left[64]:3}|{left[55]:3}|{left[46]:3}|{left[37]:3}|{left[28]:3}|{left[19]:3}|{left[10]:3}|{left[1]:3}|   |{right[73]:3}|{right[64]:3}|{right[55]:3}|{right[46]:3}|{right[37]:3}|{right[28]:3}|{right[19]:3}|{right[10]:3}|{right[1]:3}|
+---+---+---+---+---+---+---+---+---+   +---+---+---+---+---+---+---+---+---+
|{left[74]:3}|{left[65]:3}|{left[56]:3}|{left[47]:3}|{left[38]:3}|{left[29]:3}|{left[20]:3}|{left[11]:3}|{left[2]:3}|   |{right[74]:3}|{right[65]:3}|{right[56]:3}|{right[47]:3}|{right[38]:3}|{right[29]:3}|{right[20]:3}|{right[11]:3}|{right[2]:3}|
+---+---+---+---+---+---+---+---+---+   +---+---+---+---+---+---+---+---+---+
|{left[75]:3}|{left[66]:3}|{left[57]:3}|{left[48]:3}|{left[39]:3}|{left[30]:3}|{left[21]:3}|{left[12]:3}|{left[3]:3}|   |{right[75]:3}|{right[66]:3}|{right[57]:3}|{right[48]:3}|{right[39]:3}|{right[30]:3}|{right[21]:3}|{right[12]:3}|{right[3]:3}|
+---+---+---+---+---+---+---+---+---+   +---+---+---+---+---+---+---+---+---+
|{left[76]:3}|{left[67]:3}|{left[58]:3}|{left[49]:3}|{left[40]:3}|{left[31]:3}|{left[22]:3}|{left[13]:3}|{left[4]:3}|   |{right[76]:3}|{right[67]:3}|{right[58]:3}|{right[49]:3}|{right[40]:3}|{right[31]:3}|{right[22]:3}|{right[13]:3}|{right[4]:3}|
+---+---+---+---+---+---+---+---+---+   +---+---+---+---+---+---+---+---+---+
|{left[77]:3}|{left[68]:3}|{left[59]:3}|{left[50]:3}|{left[41]:3}|{left[32]:3}|{left[23]:3}|{left[14]:3}|{left[5]:3}|   |{right[77]:3}|{right[68]:3}|{right[59]:3}|{right[50]:3}|{right[41]:3}|{right[32]:3}|{right[23]:3}|{right[14]:3}|{right[5]:3}|
+---+---+---+---+---+---+---+---+---+   +---+---+---+---+---+---+---+---+---+
|{left[78]:3}|{left[69]:3}|{left[60]:3}|{left[51]:3}|{left[42]:3}|{left[33]:3}|{left[24]:3}|{left[15]:3}|{left[6]:3}|   |{right[78]:3}|{right[69]:3}|{right[60]:3}|{right[51]:3}|{right[42]:3}|{right[33]:3}|{right[24]:3}|{right[15]:3}|{right[6]:3}|
+---+---+---+---+---+---+---+---+---+   +---+---+---+---+---+---+---+---+---+
|{left[79]:3}|{left[70]:3}|{left[61]:3}|{left[52]:3}|{left[43]:3}|{left[34]:3}|{left[25]:3}|{left[16]:3}|{left[7]:3}|   |{right[79]:3}|{right[70]:3}|{right[61]:3}|{right[52]:3}|{right[43]:3}|{right[34]:3}|{right[25]:3}|{right[16]:3}|{right[7]:3}|
+---+---+---+---+---+---+---+---+---+   +---+---+---+---+---+---+---+---+---+
|{left[80]:3}|{left[71]:3}|{left[62]:3}|{left[53]:3}|{left[44]:3}|{left[35]:3}|{left[26]:3}|{left[17]:3}|{left[8]:3}|   |{right[80]:3}|{right[71]:3}|{right[62]:3}|{right[53]:3}|{right[44]:3}|{right[35]:3}|{right[26]:3}|{right[17]:3}|{right[8]:3}|
+---+---+---+---+---+---+---+---+---+   +---+---+---+---+---+---+---+---+---+
"""


    def stringify_4characters_board(squares):
        """１マスに４桁を表示できる表

        Parameters
        ----------
        squares : [81]
            ８１マスの表
        """

        return f"""\
+----+----+----+----+----+----+----+----+----+
|{squares[72]:4}|{squares[63]:4}|{squares[54]:4}|{squares[45]:4}|{squares[36]:4}|{squares[27]:4}|{squares[18]:4}|{squares[9]:4}|{squares[0]:4}|
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
