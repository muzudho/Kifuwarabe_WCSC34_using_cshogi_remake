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


    def stringify_quadruple_4characters_board(a, b, c, d):
        """１マスに４桁を表示できる表を４つ並べる

        Parameters
        ----------
        a : [81]
            ８１マスの表
        b : [81]
            ８１マスの表
        c : [81]
            ８１マスの表
        d : [81]
            ８１マスの表
        """

        return f"""\
   9    8    7    6    5    4    3    2    1            9    8    7    6    5    4    3    2    1            9    8    7    6    5    4    3    2    1            9    8    7    6    5    4    3    2    1
+----+----+----+----+----+----+----+----+----+ 　    +----+----+----+----+----+----+----+----+----+ 　    +----+----+----+----+----+----+----+----+----+ 　    +----+----+----+----+----+----+----+----+----+
|{a[72]:4}|{a[63]:4}|{a[54]:4}|{a[45]:4}|{a[36]:4}|{a[27]:4}|{a[18]:4}|{a[9]:4}|{a[0]:4}| 一    |{b[72]:4}|{b[63]:4}|{b[54]:4}|{b[45]:4}|{b[36]:4}|{b[27]:4}|{b[18]:4}|{b[9]:4}|{b[0]:4}| 一    |{c[72]:4}|{c[63]:4}|{c[54]:4}|{c[45]:4}|{c[36]:4}|{c[27]:4}|{c[18]:4}|{c[9]:4}|{c[0]:4}| 一    |{d[72]:4}|{d[63]:4}|{d[54]:4}|{d[45]:4}|{d[36]:4}|{d[27]:4}|{d[18]:4}|{d[9]:4}|{d[0]:4}| 一
+----+----+----+----+----+----+----+----+----+ 　    +----+----+----+----+----+----+----+----+----+ 　    +----+----+----+----+----+----+----+----+----+ 　    +----+----+----+----+----+----+----+----+----+
|{a[73]:4}|{a[64]:4}|{a[55]:4}|{a[46]:4}|{a[37]:4}|{a[28]:4}|{a[19]:4}|{a[10]:4}|{a[1]:4}| 二    |{b[73]:4}|{b[64]:4}|{b[55]:4}|{b[46]:4}|{b[37]:4}|{b[28]:4}|{b[19]:4}|{b[10]:4}|{b[1]:4}| 二    |{c[73]:4}|{c[64]:4}|{c[55]:4}|{c[46]:4}|{c[37]:4}|{c[28]:4}|{c[19]:4}|{c[10]:4}|{c[1]:4}| 二    |{d[73]:4}|{d[64]:4}|{d[55]:4}|{d[46]:4}|{d[37]:4}|{d[28]:4}|{d[19]:4}|{d[10]:4}|{d[1]:4}| 二
+----+----+----+----+----+----+----+----+----+ 　    +----+----+----+----+----+----+----+----+----+ 　    +----+----+----+----+----+----+----+----+----+ 　    +----+----+----+----+----+----+----+----+----+
|{a[74]:4}|{a[65]:4}|{a[56]:4}|{a[47]:4}|{a[38]:4}|{a[29]:4}|{a[20]:4}|{a[11]:4}|{a[2]:4}| 三    |{b[74]:4}|{b[65]:4}|{b[56]:4}|{b[47]:4}|{b[38]:4}|{b[29]:4}|{b[20]:4}|{b[11]:4}|{b[2]:4}| 三    |{c[74]:4}|{c[65]:4}|{c[56]:4}|{c[47]:4}|{c[38]:4}|{c[29]:4}|{c[20]:4}|{c[11]:4}|{c[2]:4}| 三    |{d[74]:4}|{d[65]:4}|{d[56]:4}|{d[47]:4}|{d[38]:4}|{d[29]:4}|{d[20]:4}|{d[11]:4}|{d[2]:4}| 三
+----+----+----+----+----+----+----+----+----+ 　    +----+----+----+----+----+----+----+----+----+ 　    +----+----+----+----+----+----+----+----+----+ 　    +----+----+----+----+----+----+----+----+----+
|{a[75]:4}|{a[66]:4}|{a[57]:4}|{a[48]:4}|{a[39]:4}|{a[30]:4}|{a[21]:4}|{a[12]:4}|{a[3]:4}| 四    |{b[75]:4}|{b[66]:4}|{b[57]:4}|{b[48]:4}|{b[39]:4}|{b[30]:4}|{b[21]:4}|{b[12]:4}|{b[3]:4}| 四    |{c[75]:4}|{c[66]:4}|{c[57]:4}|{c[48]:4}|{c[39]:4}|{c[30]:4}|{c[21]:4}|{c[12]:4}|{c[3]:4}| 四    |{d[75]:4}|{d[66]:4}|{d[57]:4}|{d[48]:4}|{d[39]:4}|{d[30]:4}|{d[21]:4}|{d[12]:4}|{d[3]:4}| 四
+----+----+----+----+----+----+----+----+----+ 　    +----+----+----+----+----+----+----+----+----+ 　    +----+----+----+----+----+----+----+----+----+ 　    +----+----+----+----+----+----+----+----+----+
|{a[76]:4}|{a[67]:4}|{a[58]:4}|{a[49]:4}|{a[40]:4}|{a[31]:4}|{a[22]:4}|{a[13]:4}|{a[4]:4}| 五    |{b[76]:4}|{b[67]:4}|{b[58]:4}|{b[49]:4}|{b[40]:4}|{b[31]:4}|{b[22]:4}|{b[13]:4}|{b[4]:4}| 五    |{c[76]:4}|{c[67]:4}|{c[58]:4}|{c[49]:4}|{c[40]:4}|{c[31]:4}|{c[22]:4}|{c[13]:4}|{c[4]:4}| 五    |{d[76]:4}|{d[67]:4}|{d[58]:4}|{d[49]:4}|{d[40]:4}|{d[31]:4}|{d[22]:4}|{d[13]:4}|{d[4]:4}| 五
+----+----+----+----+----+----+----+----+----+ 　    +----+----+----+----+----+----+----+----+----+ 　    +----+----+----+----+----+----+----+----+----+ 　    +----+----+----+----+----+----+----+----+----+
|{a[77]:4}|{a[68]:4}|{a[59]:4}|{a[50]:4}|{a[41]:4}|{a[32]:4}|{a[23]:4}|{a[14]:4}|{a[5]:4}| 六    |{b[77]:4}|{b[68]:4}|{b[59]:4}|{b[50]:4}|{b[41]:4}|{b[32]:4}|{b[23]:4}|{b[14]:4}|{b[5]:4}| 六    |{c[77]:4}|{c[68]:4}|{c[59]:4}|{c[50]:4}|{c[41]:4}|{c[32]:4}|{c[23]:4}|{c[14]:4}|{c[5]:4}| 六    |{d[77]:4}|{d[68]:4}|{d[59]:4}|{d[50]:4}|{d[41]:4}|{d[32]:4}|{d[23]:4}|{d[14]:4}|{d[5]:4}| 六
+----+----+----+----+----+----+----+----+----+ 　    +----+----+----+----+----+----+----+----+----+ 　    +----+----+----+----+----+----+----+----+----+ 　    +----+----+----+----+----+----+----+----+----+
|{a[78]:4}|{a[69]:4}|{a[60]:4}|{a[51]:4}|{a[42]:4}|{a[33]:4}|{a[24]:4}|{a[15]:4}|{a[6]:4}| 七    |{b[78]:4}|{b[69]:4}|{b[60]:4}|{b[51]:4}|{b[42]:4}|{b[33]:4}|{b[24]:4}|{b[15]:4}|{b[6]:4}| 七    |{c[78]:4}|{c[69]:4}|{c[60]:4}|{c[51]:4}|{c[42]:4}|{c[33]:4}|{c[24]:4}|{c[15]:4}|{c[6]:4}| 七    |{d[78]:4}|{d[69]:4}|{d[60]:4}|{d[51]:4}|{d[42]:4}|{d[33]:4}|{d[24]:4}|{d[15]:4}|{d[6]:4}| 七
+----+----+----+----+----+----+----+----+----+ 　    +----+----+----+----+----+----+----+----+----+ 　    +----+----+----+----+----+----+----+----+----+ 　    +----+----+----+----+----+----+----+----+----+
|{a[79]:4}|{a[70]:4}|{a[61]:4}|{a[52]:4}|{a[43]:4}|{a[34]:4}|{a[25]:4}|{a[16]:4}|{a[7]:4}| 八    |{b[79]:4}|{b[70]:4}|{b[61]:4}|{b[52]:4}|{b[43]:4}|{b[34]:4}|{b[25]:4}|{b[16]:4}|{b[7]:4}| 八    |{c[79]:4}|{c[70]:4}|{c[61]:4}|{c[52]:4}|{c[43]:4}|{c[34]:4}|{c[25]:4}|{c[16]:4}|{c[7]:4}| 八    |{d[79]:4}|{d[70]:4}|{d[61]:4}|{d[52]:4}|{d[43]:4}|{d[34]:4}|{d[25]:4}|{d[16]:4}|{d[7]:4}| 八
+----+----+----+----+----+----+----+----+----+ 　    +----+----+----+----+----+----+----+----+----+ 　    +----+----+----+----+----+----+----+----+----+ 　    +----+----+----+----+----+----+----+----+----+
|{a[80]:4}|{a[71]:4}|{a[62]:4}|{a[53]:4}|{a[44]:4}|{a[35]:4}|{a[26]:4}|{a[17]:4}|{a[8]:4}| 九    |{b[80]:4}|{b[71]:4}|{b[62]:4}|{b[53]:4}|{b[44]:4}|{b[35]:4}|{b[26]:4}|{b[17]:4}|{b[8]:4}| 九    |{c[80]:4}|{c[71]:4}|{c[62]:4}|{c[53]:4}|{c[44]:4}|{c[35]:4}|{c[26]:4}|{c[17]:4}|{c[8]:4}| 九    |{d[80]:4}|{d[71]:4}|{d[62]:4}|{d[53]:4}|{d[44]:4}|{d[35]:4}|{d[26]:4}|{d[17]:4}|{d[8]:4}| 九
+----+----+----+----+----+----+----+----+----+ 　    +----+----+----+----+----+----+----+----+----+ 　    +----+----+----+----+----+----+----+----+----+ 　    +----+----+----+----+----+----+----+----+----+"""
