#!/bin/bash

# Läs in variabler från .env
ENV_FILE=".env"
if [[ -f $ENV_FILE ]]; then
    source $ENV_FILE
else
    echo "Error: .env-fil saknas. Skapa en .env-fil med nödvändiga variabler."
    exit 1
fi



# Stoppa alla effekter
stop_effects() {
  curl -X POST -H "Content-Type: application/json" -d "{\"password\": \"$PASSWORD\"}" $IP/stop_effects
  echo "All LED effects stopped."
}

# Starta rullande våg (Forward eller Backward)
set_wave() {
  COLOR=$1          # Färg (blue, red, green)
  DIRECTION=$2      # Direction (forward, backward)
  curl -X POST -H "Content-Type: application/json" -d "{\"password\": \"$PASSWORD\", \"color\": \"$COLOR\", \"direction\": \"$DIRECTION\"}" $IP/set_wave
  echo "Started rolling wave with color $COLOR and direction $DIRECTION."
}

# Starta blinkande effekt
set_blink() {
  COLOR=$1          # Färg (blue, red, green)
  SPEED=$2          # Blinkhastighet (1 = snabb, 5 = långsam)
  curl -X POST -H "Content-Type: application/json" -d "{\"password\": \"$PASSWORD\", \"color\": \"$COLOR\", \"speed\": $SPEED}" $IP/set_blink
  echo "Started blinking effect with color $COLOR and speed $SPEED."
}


checkgoogle() {
    STATUS_CODE=$(curl -L -o /dev/null -s -w "%{http_code}" "$GURL")
    [[ "$STATUS_CODE" -eq 200 ]] && echo "True" || echo "False"
}

check_gbg() {
    for _ in {1..2}; do
        RESPONSE=$(curl -L -s "$URL")
        if echo "$RESPONSE" | grep -q "Sajten uppe!"; then
            echo "True"
            return
        else
          echo "Inte bra" 
        fi
        sleep $SLEEP
    done
    echo "False"
}

handle_dns_name() {
    DNS_NAME=$($CHECK_GBG)
    if [[ $DNS_NAME == *"green"* ]]; then
        set_wave "green" "forward"
        echo "Green"
    elif [[ $DNS_NAME == *"blue"* ]]; then
        set_wave "blue" "forward"
        echo "Blue"
    else
        echo "none"
    fi
}

# Huvudflöde
GOCHECK=$(checkgoogle)
if [[ $GOCHECK == "False" ]]; then
    echo "Kan inte nå Google, startar om WiFi."
    stop_effects
    sudo systemctl restart networking.service
    sleep $SLEEP
    GOCHECK=$(checkgoogle)
    if [[ $GOCHECK == "False" ]]; then
        echo "Kan fortfarande inte nå Google, rebootar systemet."
        stop_effects
        reboot
        exit
    else
        echo "WiFi är uppe, Google fungerar."
    fi
else
    echo "Google fungerar."
    #Run GBG check
    if [[ $1 == "on" ]]; then
        if [[ $(check_gbg) == "True" ]]; then
            check_status=$(handle_dns_name)
            echo $check_status
            if [[ $check_status == "none" ]]; then
              echo "Hittar ingen färg"
              stop_effects
            fi
        else 
            echo "Inte bra" 
            set_blink "red" 2

        fi

    elif [[ $1 == "off" ]]; then
        echo "Stänger av LED."
        curl $CURL_OPTIONS $LED_OFF > /dev/null
        stop_effects
    fi
fi
