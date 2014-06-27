var angularApp = angular.module('angularApp', ['ngResource']);

angularApp.config(function ($httpProvider) {
    $httpProvider.defaults.headers.post['X-CSRFToken'] = csrftoken;
    $httpProvider.defaults.headers.common['X-CSRFToken'] = $httpProvider.defaults.headers.post['X-CSRFToken'];
    $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
});
