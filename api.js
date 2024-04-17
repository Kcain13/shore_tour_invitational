class GhinDataService {
    async getUserToken(user, pwd) {
        try {
            const response = await fetch("/api/golfer_login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    user: user,
                    password: pwd,
                }),
            });
            const data = await response.json();
            return data.token;
        } catch (error) {
            console.error("Error fetching user token:", error);
            throw error;
        }
    }

    async getUserCourseHandicap(GHIN, user_token) {
        try {
            const formattedDate = this.formatDate(new Date());
            const response = await fetch(`/api/course_handicaps?golfer_id=${GHIN}`, {
                headers: {
                    Authorization: `Bearer ${user_token}`,
                },
            });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error("Error fetching user course handicap:", error);
            throw error;
        }
    }

    async getUserHandicap(GHIN, user_token) {
        try {
            const response = await fetch(`/api/golfers?golfer_id=${GHIN}`, {
                headers: {
                    Authorization: `Bearer ${user_token}`,
                },
            });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error("Error fetching user handicap:", error);
            throw error;
        }
    }

    formatDate(date) {
        const year = date.getFullYear();
        let month = (date.getMonth() + 1).toString().padStart(2, "0");
        let day = date.getDate().toString().padStart(2, "0");
        return [year, month, day].join("-");
    }
}

export default new GhinDataService();
