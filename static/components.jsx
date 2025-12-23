const Message = function (props) {
    return (
        <div>Message Component</div>
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

const MessageInput = function (props) {
    const { url } = props;
    return (
        <form action={url} method="POST">
            <input type="text" className="input" placeholder="Type a message..." name="message" />
            <button type="submit">Send</button>
        </form>
    );
};

const ChatList = function (props) {
    const { list } = props;
    if (!list || !Array.isArray(list) || list.length === 0) {
        return (
            <div>
                <p>No chats found. Create a Conversation!</p>
                <Button text="Create a Conversation" redirect="/create_chat" />
            </div>
        );
    }
    const handleChatClick = (chatId) => {
        window.location.href = `/chat/${chatId}`;
    };
    return (
        <div>
            <table>
                <tbody>
                    {list.map((chat) => (
                        <tr
                            key={chat.id}
                            className={chat.read ? 'read' : 'unread'}
                            onClick={() => handleChatClick(chat.id)}
                        >
                            <td>{chat.name}</td>
                            <td>{chat.lastMessage || (chat.latest_message && chat.latest_message.message) || ''}</td>
                            <td>{chat.timestamp || (chat.latest_message && chat.latest_message.timestamp) || ''}</td>
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

    const handleUserDeselect = (userId) => {
        setSelectedUsers(selectedUsers.filter(u => u.id !== userId));
    };

    return (
        <div>
            <div style={{ position: 'relative', marginBottom: '1rem' }}>
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
                    style={{ marginBottom: '0.5rem' }}
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
                <div style={{ marginBottom: '1rem' }}>
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
                <input name="name" type="text" placeholder="Chat Name (optional)" />
                <input name="message" type="text" placeholder="First Message (optional)" />
                <button type="submit" className="btn btn-primary">Create Chat</button>
            </form>
        </div>
    );
};

