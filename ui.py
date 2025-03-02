from pleasesetuphere import log_file_path, ip_address
import pandas as pd
import streamlit as st
from dataplot import read_log_file, filter_logs, plot_combined_access_data
from airesponses import readai, filterai, analyze_ai, concerning_hours, concerning_websites, summary_preferences


# Main ui

# session state cached for speed
if "selected_website" not in st.session_state:
    st.session_state["selected_website"] = "tiktok.com"
if "sort_by" not in st.session_state:
    st.session_state["sort_by"] = "Visits (Descending)"

@st.cache_data
def load_and_filter_logs(file_path, websites, ip_address):
    logs = read_log_file(file_path)
    return filter_logs(logs, websites, ip_address)

# Function to estimate time spent
def estimate_time_spent(access_counts, time_per_access_minutes=0.2):
    time_spent_data = []
    for website, counts in access_counts.items():
        total_accesses = sum(counts)
        estimated_time = total_accesses * time_per_access_minutes / 60  # Convert to hours
        time_spent_data.append({
            "Website": website,
            "Total Accesses": total_accesses,
            "Estimated Time (Hours)": round(estimated_time, 2),
        })
    return pd.DataFrame(time_spent_data)

# Main UI
def main():
    st.title("Network Data")
    st.write("built by isaac")

    # File and settings
    websites = ["tiktok.com", "instagram.com", "youtube.com"] #change this to the websites u wanna see

    # Load logs and access counts
    access_counts = load_and_filter_logs(log_file_path, websites, ip_address)

    # Plot bar graph
    st.write("### Visits per Hour:")
    plot = plot_combined_access_data(access_counts)
    st.pyplot(plot)

    # Sort button
    st.write("### Data Tables by Website")
    st.session_state["sort_by"] = st.radio(
        "Sort data by:",
        ("Hour (Ascending)", "Visits (Descending)"),
        index=0 if st.session_state["sort_by"] == "Hour (Ascending)" else 1,
        key="sort_by_radio",
    )

    # Display separate tables for each website
    num_websites = len(websites)
    columns = st.columns(num_websites)

    for i, (website, counts) in enumerate(access_counts.items()):
        with columns[i]:
            st.write(f"### {website.capitalize()}")
            raw_data = [{"Hour": hour, "Visits": count} for hour, count in enumerate(counts)]
            raw_data_df = pd.DataFrame(raw_data)

            # Apply sorting from session state
            if st.session_state["sort_by"] == "Hour (Ascending)":
                raw_data_df = raw_data_df.sort_values(by="Hour", ascending=True)
            else:
                raw_data_df = raw_data_df.sort_values(by="Visits", ascending=False)

            st.dataframe(raw_data_df)

    # Estimate total time spent
    st.write("### Estimated Total Time Spent on Websites")
    time_spent_df = estimate_time_spent(access_counts, 0.2)
    st.dataframe(time_spent_df)

    # Hourly estimated time spent
    st.write("### Hourly Estimated Time Spent")
    st.session_state["selected_website"] = st.selectbox(
        "Select a Website:",
        websites,
        index=websites.index(st.session_state["selected_website"]),
    )
    hourly_time_spent = [{"Hour": hour, "Estimated Time (Minutes)": count * 0.2} for hour, count in enumerate(access_counts[st.session_state["selected_website"]])]
    hourly_time_spent_df = pd.DataFrame(hourly_time_spent)

    st.dataframe(hourly_time_spent_df)
    
    st.write("### AI overview")
    if st.button("AI overview"):
        try:
            logs = readai(log_file_path)
            filtered_logs = filterai(logs, concerning_websites, concerning_hours)
            if filtered_logs:
                result = analyze_ai(filtered_logs)
                st.write(result)
        except Exception as e:
            st.write("You need a Groq API key to run this. ", e)
if __name__ == "__main__":
    main()

