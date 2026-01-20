const apiKey = process.env.USDA_API_KEY || "X83kuLJUEwAjZc4v9smF9dxVUfk2BbWVWlNb4Cgh";

async function testFetch(text) {
    const url = new URL("https://api.nal.usda.gov/fdc/v1/foods/search");
    url.searchParams.append("api_key", apiKey);
    url.searchParams.append("query", text);
    url.searchParams.append("pageSize", "3");

    const dataTypes = ["Survey (FNDDS)", "Foundation", "SR Legacy", "Branded"];
    dataTypes.forEach(type => url.searchParams.append("dataType", type));

    console.log("Fetching URL:", url.toString());

    try {
        const response = await fetch(url.toString());
        const data = await response.json();
        console.log(`Results for '${text}':`, data.totalHits);
        if (data.foods && data.foods.length > 0) {
            console.log("First match:", data.foods[0].description);
        }
    } catch (e) {
        console.error("Error:", e);
    }
}

testFetch("scrambled eggs");
