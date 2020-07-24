#!/usr/bin/env runclj
^{:runclj {:browser-mode true
           :lein [[org.clojure/clojure "1.10.1"]
                  [org.clojure/clojurescript "1.10.764"]
                  [garden "1.3.10"]
                  [funcool/bide "1.6.0"]
                  [reagent "1.0.0-alpha2"]]}}
(ns client
  (:require [reagent.dom :as reagent.dom]
            [reagent.core :as reagent]
            [bide.core :as bide]
            [garden.core :as garden]
            [clojure.browser.repl :as repl]))

(defonce state
  (reagent/atom
   {:page home
    :page1 {:state 0}}))

(def style
  (garden/css
   [:body {:font-family "helvetica"}]
   [:p {:font-size "16px"}]
   [:div#content {:margin-left "5px"}]
   [:a {:margin "5px"
        :color "purple"
        :text-decoration "none"}]
   [:a:hover {:text-decoration "underline"}]))

(defn root []
  [:div
   [:style style]
   [:p
    [:a#home   {:href "#/"} "home"]
    [:a#page1  {:href "#/page1"} "page 1"]
    [:a#broken {:href "#/nothing-to-see/here"} "broken link"]]
   [:hr]
   [:div#content
    [(:page @state)]]])

(defn home []
  [:p "home page"])

(defn page1 []
  [:div
   [:p "this is a page with some data: " (-> @state :page1 :state)]
   [:p [:input {:type "button"
                :value "push me"
                :on-click #(swap! state update-in [:page1 :state] inc)}]]])

(defn not-found []
  [:p "404"])

(def router
  [["/" home]
   ["/page1" page1]
   ["(.*)" not-found]])

(defn -main []
  (defonce repl (repl/connect "http://localhost:9000/repl")) ;; localhost for laptop, or an ipv4 address to repl against a mobile browser
  (bide/start! (bide/router router) {:default home :on-navigate #(swap! state assoc :page %) :html5? false})
  (reagent.dom/render [root] (js/document.getElementById "app")))
