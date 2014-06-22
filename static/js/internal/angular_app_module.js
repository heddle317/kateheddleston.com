var angularApp = angular.module('angularApp', ['ngResource']);

angularApp.config(function ($httpProvider) {
    $httpProvider.defaults.headers.post['X-CSRFToken'] = csrftoken;
});
