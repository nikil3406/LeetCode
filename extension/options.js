const apiUrl=document.getElementById("apiUrl");
const archiveToken=document.getElementById("archiveToken");
const status=document.getElementById("status");

chrome.storage.local.get({apiUrl:"",archiveToken:""},v=>{
  apiUrl.value=v.apiUrl; archiveToken.value=v.archiveToken;
});

document.getElementById("save").onclick=async()=>{
  await chrome.storage.local.set({
    apiUrl:apiUrl.value.trim(),
    archiveToken:archiveToken.value.trim()
  });
  status.textContent="Saved.";
};