#!/usr/bin/env runclj
^{:runclj {:browser-mode true
           :lein [[org.clojure/clojure "1.10.3"]
                  [org.clojure/clojurescript "1.10.879"]
                  [garden "1.3.10"]
                  [funcool/bide "1.7.0"]
                  [reagent "1.1.0"]
                  [arttuka/reagent-material-ui "4.11.3-2"]
                  [cljsjs/react "17.0.2-0"]
                  [cljsjs/react-dom "17.0.2-0"]]}}

(ns client
  (:require [cljs.pprint :as pp]
            [reagent.dom :as reagent.dom]
            [reagent.core :as reagent]
            [bide.core :as bide]
            [garden.core :as garden]
            [clojure.browser.repl :as repl]
            [reagent-material-ui.core.button :refer [button]]
            [reagent-material-ui.core.card :refer [card]]
            [reagent-material-ui.core.app-bar :refer [app-bar]]
            [reagent-material-ui.core.toolbar :refer [toolbar]]
            [reagent-material-ui.core.typography :refer [typography]]
            [reagent-material-ui.core.container :refer [container]]))


;; a global do block makes the browser repl workflow more convenient
;; by invoking (-main) no matter which form was evaluated.
(do

  (set! *warn-on-infer* true)

  (defonce state
    (reagent/atom
     {:page nil
      :page1 {:state 0}}))

  (def style
    (garden/css
     [:body {:background-color "rgb(240, 240, 240)"}]
     ["*" {:font-family "monospace !important"}]
     [:.MuiIconButton-root {:border-radius "10%"}]
     [:.MuiAppBar-colorPrimary {:background-color "rgb(230, 230, 230)"}]))

  (defn component-menu-button [page-name href]
    [button {:href href
             :id page-name}
     page-name])

  (defn component-root []
    [:<>
     [:style style]
     [app-bar {:position "static"}
      [toolbar
       [component-menu-button "home" "#/"]
       [component-menu-button "page-1" "#/page1"]
       [component-menu-button "broken-link" "#/nothing-to-see/here"]]]
     [container {:id "content"
                 :style {:padding 0
                         :margin-top "10px"}}
      (when-let [page (:page @state)]
        [page])]])

  (defn component-home []
    [card {:style {:padding "5px"}}
     [typography {:style {:margin "5px"}}
      "home page"]])

  (defn component-page1 []
    [card {:style {:padding "5px"}}
     [typography {:style {:margin "5px"}}
      "this is a page with some data: " (-> @state :page1 :state)]
     [button {:style {:background-color "rgb(200,200,200)"
                      :margin "5px"}
              :on-click #(swap! state update-in [:page1 :state] inc)}
      "push me"]])

  (defn component-not-found []
    [card {:style {:padding "5px"}}
     [typography {:style {:margin "5px"}}
      "404"]])

  (def router
    [["/" component-home]
     ["/page1" component-page1]
     ["(.*)" component-not-found]])

  (defn -main []
    (defonce repl (repl/connect "http://localhost:9000/repl")) ;; localhost for laptop, or an ipv4 address to repl against a mobile browser. this line is automatically removed from the release build.
    (bide/start! (bide/router router) {:default component-home
                                       :on-navigate #(swap! state assoc :page %)
                                       :html5? false})
    (reagent.dom/render [component-root] (js/document.getElementById "app")))

  ;; trigger re-render for browser repl workflow
  (-main))
