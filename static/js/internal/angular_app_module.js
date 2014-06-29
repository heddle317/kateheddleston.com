var angularApp = angular.module('angularApp', ['ngResource', 'ngSanitize']);

angularApp.config(function ($interpolateProvider, $httpProvider) {
    $interpolateProvider.startSymbol('{[{');
    $interpolateProvider.endSymbol('}]}');
    $httpProvider.defaults.headers.post['X-CSRFToken'] = csrftoken;
    $httpProvider.defaults.headers.common['X-CSRFToken'] = $httpProvider.defaults.headers.post['X-CSRFToken'];
    $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
});
