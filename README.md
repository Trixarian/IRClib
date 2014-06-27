IRClib
======

IRClib is a Portable Multi-Client Asynchronous Python IRC library with minimal protocol abstraction.


Why use yet another IRC lib?
----------------------------

If you tried other IRC libraries before, you may haved found that most didn't work with all IRCd or some were too dependecy heavy to make scripts written with it easy to port from system to system. Another problem you may have noticed is that that all the other libraries rely too much on abstraction - even to the point of making writing a quick IRCBot script a small mine field of finding what something is called within it.

That's why I wanted something that could generate as many clients as needed, as simply as possibe without getting in the way. This is the result. In fact, you can generate a simple IRC client that joins a channel in two lines of code. This may sound impressive, but using a simple for each loop, you can essentially add as many IRC clients as you want in those two lines too. Sounds way more interesting now, doesn't it?

Each time you call the class it will generate a new IRC Client instance. It manages the loops internally, so by just providing it with the basics, it will do all the rest for you. On top of that, each client has it's own parser that can be hooked into using a simple function within your own script and passing it to the class. The client's internal parser will then forward the object and raw data to your one, giving you direct access to it's information and allowing you to keep track of and control each client at will. Throw in some basic IRC aliases that any normal IRC user would be familiar with, and you suddenly have an easy and powerful way to write your IRC Bots. Best of all, it's all done without needing threading at all.

For now, there isn't much in the way of Documentation, but you can read through the comments in the code and example.py to get the basic idea how to use it. On my TODO list is adding OpenSSL, DCC and better documentation to this script. Maybe even an asynchronous timer at some point, so watch this space.


License
-------

This code is released under the Creative Commons Zero license, which places it in the Public Domain while obsolving me of any responsibility or liablity that may result from the use or misuse of this code. Basically put, you have the full right to do whatever you want with the code without any restrictions including selling and relicensing it as your own. The only thing you cannot do is sue me if things go wrong. Read LICENSE for more information on this.
