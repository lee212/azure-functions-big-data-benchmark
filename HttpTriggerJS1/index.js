module.exports = function (context, req) {
    context.log('[v5-restoring-0M] Start of JS through HTTP');

    if (req.query.name || (req.body && req.body.name)) {
        context.res = {
            // status: 200, /* Defaults to 200 */
            body: "Version 5 " + (req.query.name || req.body.name)
        };
    }
    context.done();
};
