import './SearchBar.css';

const SearchBar = ({ value, onChange, placeholder = 'Search colleges, courses or cities' }) => {
  return (
    <div className="search-shell">
      <input
        type="text"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        className="search-input"
      />
      <button type="button" className="search-button">
        Search
      </button>
    </div>
  );
};

export default SearchBar;
