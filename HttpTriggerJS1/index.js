module.exports = function (context, req) {
    context.log('[v2] Start of JS through HTTP');

    if (req.query.name || (req.body && req.body.name)) {
        context.res = {
            // status: 200, /* Defaults to 200 */
            body: "Version 2 " + (req.query.name || req.body.name)
        };
    }
    context.done();
};
