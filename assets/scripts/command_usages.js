function main() {
    return Events(params)
        .filter(function(e) {
            return e.name == 'Command Used'
        })
        .groupBy(["properties.server"], mixpanel.reducer.count());
}