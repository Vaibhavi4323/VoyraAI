function LoadingState() {
  return (
    <div style={{
      textAlign: "center",
      marginTop: "40px"
    }}>
      <div style={{
        width: "60px",
        height: "60px",
        border: "6px solid #ddd",
        borderTop: "6px solid #3b82f6",
        borderRadius: "50%",
        animation: "spin 1s linear infinite",
        margin: "0 auto"
      }} />

      <h3 style={{ marginTop: "20px" }}>
        Generating your itinerary...
      </h3>

      <p style={{ color: "#666" }}>
        Our AI is crafting the perfect travel plan for you
      </p>

      {/* Spinner animation */}
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
}

export default LoadingState;