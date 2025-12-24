const Message = function (props) {
    const { id, user_id, username, message, timestamp } = props;

    // Format timestamp to be human-readable
    const formatTimestamp = (timestampStr) => {
        if (!timestampStr) return '';
        try {
            const date = new Date(timestampStr);
            const now = new Date();
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMs / 3600000);
            const diffDays = Math.floor(diffMs / 86400000);

            // If less than a minute ago
            if (diffMins < 1) return 'Just now';
            // If less than an hour ago
            if (diffMins < 60) return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
            // If less than a day ago
            if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
            // If less than a week ago
            if (diffDays < 7) return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;

            // Otherwise show full date and time
            return date.toLocaleString('en-US', {
                month: 'short',
                day: 'numeric',
                year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
                hour: 'numeric',
                minute: '2-digit',
                hour12: true
            });
        } catch (e) {
            return timestampStr;
        }
    };

    return (
        <div className="message-container">
            <div>
                <strong>
                    {username || 'Unknown User'}
                </strong>
                <span>
                    {formatTimestamp(timestamp)}
                </span>
            </div>
            <div>
                {message}
            </div>
            <div>
                ID: {id} | User ID: {user_id}
            </div>
        </div>
    );
};

const Button = function (props) {
    const { text, redirect } = props;
    const handleClick = () => {
        window.location.href = redirect;
    };
    return (
        <button
            onClick={handleClick}
            className="btn btn-primary btn-lg"
        >
            {text}
        </button>
    );
};

const ChatList = function (props) {
    const { list } = props;
    const [chatList, setChatList] = React.useState(list || []);

    // Handle empty chats list
    if (!chatList || !Array.isArray(chatList) || chatList.length === 0) {
        return (
            <div>
                <p>No chats found. Create a Conversation!</p>
            </div>
        );
    }
    const handleChatClick = (chatId) => {
        window.location.href = `/chat/${chatId}`;
    };

    const handleDelete = async (e, chatId) => {
        e.stopPropagation();
        const confirmed = window.confirm('Are you sure you want to delete this chat?');
        if (!confirmed) return;

        try {
            const response = await fetch('/delete_chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ chat_id: chatId })
            });

            if (!response.ok) {
                throw new Error('Failed to delete chat');
            }

            setChatList(prev => prev.filter(chat => chat.id !== chatId));
        } catch (error) {
            console.error('Delete chat error:', error);
            alert('Could not delete chat. Please try again.');
        }
    };
    return (
        <div>
            <table>
                <tbody>
                    {chatList.map((chat) => (
                        <tr
                            key={chat.id}
                            className={chat.read ? 'read' : 'unread'}
                            onClick={() => handleChatClick(chat.id)}
                        >
                            <td>{chat.name}</td>
                            <td>{chat.lastMessage || (chat.latest_message && chat.latest_message.message) || ''}</td>
                            <td>{chat.timestamp || (chat.latest_message && chat.latest_message.timestamp) || ''}</td>
                            <td>
                                <button
                                    type="button"
                                    className="btn btn-danger btn-sm"
                                    onClick={(e) => handleDelete(e, chat.id)}
                                >
                                    Delete
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

const Search = function (props) {
    const [searchQuery, setSearchQuery] = React.useState('');
    const [searchResults, setSearchResults] = React.useState([]);
    const [selectedUsers, setSelectedUsers] = React.useState([]);
    const [showResults, setShowResults] = React.useState(false);

    // Debounce search query
    React.useEffect(() => {
        if (!searchQuery.trim()) {
            setSearchResults([]);
            setShowResults(false);
            return;
        }

        const timeoutId = setTimeout(() => {
            fetch(`/search_users?q=${encodeURIComponent(searchQuery)}`)
                .then(response => response.json())
                .then(data => {
                    setSearchResults(data);
                    setShowResults(true);
                })
                .catch(error => {
                    console.error('Search error:', error);
                    setSearchResults([]);
                });
        }, 300);

        return () => clearTimeout(timeoutId);
    }, [searchQuery]);

    const handleUserSelect = (user) => {
        // Check if user is already selected
        if (!selectedUsers.find(u => u.id === user.id)) {
            setSelectedUsers([...selectedUsers, user]);
        }
        setSearchQuery('');
        setShowResults(false);
    };

    // if user clicks the 'x' on a selected user
    const handleUserDeselect = (userId) => {
        setSelectedUsers(selectedUsers.filter(u => u.id !== userId));
    };

    return (
        <div>
            <div>
                <input
                    type="text"
                    className="form-control"
                    placeholder="Search for users..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onFocus={() => searchQuery && setShowResults(true)}
                    onBlur={() => {
                        // Delay hiding to allow click on results
                        setTimeout(() => setShowResults(false), 200);
                    }}
                />
                {showResults && searchQuery.trim() && (
                    <div>
                        {searchResults.length > 0 ? (
                            searchResults.map((user) => (
                                <div
                                    key={user.id}
                                    onClick={() => handleUserSelect(user)}
                                    onMouseEnter={(e) => e.target.style.backgroundColor = '#f0f0f0'}
                                    onMouseLeave={(e) => e.target.style.backgroundColor = 'white'}
                                >
                                    {user.username}
                                </div>
                            ))
                        ) : (
                            <div>
                                No users found.
                            </div>
                        )}
                    </div>
                )}
            </div>

            {selectedUsers.length > 0 && (
                <div>
                    <label>Selected Users:</label>
                    <div>
                        {selectedUsers.map((user) => (
                            <span key={user.id}>
                                {user.username}
                                <button type="button" onClick={() => handleUserDeselect(user.id)}>
                                    ×
                                </button>
                            </span>
                        ))}
                    </div>
                </div>
            )}

            <form method="post" action="/create_chat">
                {/* Hidden inputs for selected users */}
                {selectedUsers.map((user) => (
                    <input
                        key={user.id}
                        type="hidden"
                        name="selected_users"
                        value={user.id}
                    />
                ))}
                <input className="form-control" name="name" type="text" placeholder="Chat Name (optional)" />
                <input className="form-control" name="message" type="text" placeholder="First Message (optional)" />
                <button type="submit" className="btn btn-primary">Create Chat</button>
            </form>
        </div>
    );
};

const ChatRoom = function (props) {
    const { chatId, initialMessages } = props;
    const [messages, setMessages] = React.useState(initialMessages || []);
    const [messageInput, setMessageInput] = React.useState('');
    const messagesEndRef = React.useRef(null);

    // Initialize Socket.IO connection
    React.useEffect(() => {
        const socket = io();

        // Join the chat room
        socket.emit('join_room', { room: String(chatId) });

        // Listen for new messages
        socket.on('new_message', (data) => {
            setMessages(prevMessages => [...prevMessages, data]);
        });

        // Cleanup on unmount
        return () => {
            socket.emit('leave_room', { room: String(chatId) });
            socket.disconnect();
        };
    }, [chatId]);

    // Scroll to bottom when new messages arrive
    React.useEffect(() => {
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [messages]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!messageInput.trim()) return;

        const messageToSend = messageInput.trim();
        setMessageInput(''); // Clear input immediately

        // Send message via fetch
        const formData = new FormData();
        formData.append('chat_id', chatId);
        formData.append('message', messageToSend);

        try {
            const response = await fetch('/send_message', {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            });

            // The server will emit the message via Socket.IO, so we don't need to update state here
            // Socket.IO will handle updating the UI with the new message
        } catch (error) {
            console.error('Error sending message:', error);
            // Restore the message input on error
            setMessageInput(messageToSend);
            alert('Failed to send message. Please try again.');
        }
    };

    return (
        <div>
            <div>
                {messages.length === 0 ? (
                    <div>
                        <p>No messages yet. Start the conversation!</p>
                    </div>
                ) : (
                    messages.map((msg) => (
                        <Message
                            key={msg.id}
                            id={msg.id}
                            user_id={msg.user_id}
                            username={msg.username}
                            message={msg.message}
                            timestamp={msg.timestamp}
                        />
                    ))
                )}
                <div ref={messagesEndRef} />
            </div>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    className="form-control"
                    placeholder="Type a message..."
                    value={messageInput}
                    onChange={(e) => setMessageInput(e.target.value)}
                />
                <button type="submit" className="btn btn-primary">
                    Send
                </button>
            </form>
        </div>
    );
};

